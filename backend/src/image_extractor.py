import zipfile
import os
import re
import base64
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field

from config import EXTRACTED_DIR, GROQ_API_KEY, VISION_MODEL

# Defined locally since the global config prompt was disabled
IMAGE_DESCRIPTION_PROMPT = """Describe this image from a patent document in detail.
Focus on:
- Physical structure, layers, and geometry
- Materials and compositions visible
- Labels, numbered components, and annotations
- Measurements, dimensions, or scale indicators
- Charts/graphs: axes, data trends, and key values
- Any text or captions visible in the image

Surrounding document context: {surrounding_text}

Provide a concise but thorough technical description (2-4 sentences)."""

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

logger = logging.getLogger(__name__)


@dataclass
class ExtractedImage:
    image_id: str
    filename: str
    filepath: str
    original_format: str
    section: str
    surrounding_text: str
    vision_description: str = ""


class ImageExtractor:

    def __init__(self, output_dir: Path = None, use_vision: bool = True):
        self.output_dir = output_dir or EXTRACTED_DIR
        self.use_vision = use_vision and HAS_LANGCHAIN and bool(GROQ_API_KEY)

    def extract(self, docx_path: str | Path, doc_label: str = "DOC") -> list[ExtractedImage]:
        docx_path = Path(docx_path)
        doc_output = self.output_dir / doc_label
        doc_output.mkdir(parents=True, exist_ok=True)

        zf = zipfile.ZipFile(str(docx_path))
        media_files = [n for n in zf.namelist() if "media/" in n]

        image_id_map = self._build_image_paragraph_map(zf)
        paragraph_texts = self._get_paragraph_texts(zf)

        extracted = []
        vision_tasks = []

        for media_path in media_files:
            fname = os.path.basename(media_path)
            ext = os.path.splitext(fname)[1].lower()
            data = zf.read(media_path)

            saved_path = doc_output / fname
            with open(saved_path, "wb") as out:
                out.write(data)

            png_path = saved_path
            if ext in [".emf", ".wmf"] and HAS_PIL:
                try:
                    img = Image.open(io.BytesIO(data))
                    png_name = os.path.splitext(fname)[0] + ".png"
                    png_path = doc_output / png_name
                    img.save(str(png_path), "PNG")
                except Exception:
                    pass

            image_key = os.path.splitext(fname)[0]
            surrounding = image_id_map.get(image_key, "")
            if not surrounding and image_key in paragraph_texts:
                surrounding = paragraph_texts.get(image_key, "")

            section = self._guess_section(surrounding)
            final_path = str(png_path if png_path.exists() else saved_path)

            extracted.append({
                "image_id": f"{doc_label}_{image_key}",
                "filename": fname,
                "filepath": final_path,
                "original_format": ext,
                "section": section,
                "surrounding": surrounding,
            })

            if self.use_vision and ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                vision_tasks.append({
                    "index": len(extracted) - 1,
                    "filepath": final_path,
                    "surrounding": surrounding
                })

        zf.close()

        # Run vision LLM calls in parallel
        if vision_tasks:
            logger.info(f"Running {len(vision_tasks)} Vision LLM calls in parallel...")
            import concurrent.futures
            
            def get_vision_desc(task):
                return task["index"], self._describe_with_vision(task["filepath"], task["surrounding"])
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = executor.map(get_vision_desc, vision_tasks)
                
                for idx, desc in results:
                    extracted[idx]["vision_desc"] = desc

        # Build final ExtractedImage objects
        final_extracted = []
        for item in extracted:
            vision_desc = item.get("vision_desc", "")
            surrounding = item["surrounding"]
            
            combined_text = surrounding
            if vision_desc:
                combined_text = f"{surrounding}\n[Vision Description]: {vision_desc}" if surrounding else vision_desc

            final_extracted.append(ExtractedImage(
                image_id=item["image_id"],
                filename=item["filename"],
                filepath=item["filepath"],
                original_format=item["original_format"],
                section=item["section"],
                surrounding_text=combined_text[:800],
                vision_description=vision_desc,
            ))

        return final_extracted

    def _build_image_paragraph_map(self, zf: zipfile.ZipFile) -> dict[str, str]:
        """Extract surrounding text for each image by parsing document XML.
        
        Looks both BACKWARD and FORWARD from the image paragraph to find
        the best context text, handling cases where the description appears
        after the image (e.g., in table cells).
        """
        mapping = {}
        try:
            xml_content = zf.read("word/document.xml")
            root = ET.fromstring(xml_content)

            wml = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            blip_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"

            # Collect all paragraphs first so we can look forward
            paragraphs = list(root.iter(f"{{{wml}}}p"))

            # Extract text for each paragraph
            para_texts = []
            for p_elem in paragraphs:
                texts = []
                for t_elem in p_elem.iter(f"{{{wml}}}t"):
                    if t_elem.text:
                        texts.append(t_elem.text)
                para_texts.append("".join(texts))

            # Find images and map to surrounding text
            all_text = ""
            for i, p_elem in enumerate(paragraphs):
                para_text = para_texts[i]

                for blip in p_elem.iter(f"{{{blip_ns}}}blip"):
                    embed_id = blip.get(f"{{{rel_ns}}}embed", "")
                    if not embed_id:
                        continue

                    if para_text.strip():
                        # Case 1: Image paragraph itself has text
                        context = para_text
                    else:
                        # Case 2: Image-only paragraph — look FORWARD first
                        forward_text = []
                        for j in range(i + 1, min(i + 4, len(paragraphs))):
                            next_text = para_texts[j].strip()
                            if next_text:
                                forward_text.append(next_text)
                                # Stop after collecting enough context
                                if len(" ".join(forward_text)) > 200:
                                    break

                        if forward_text:
                            # Prefer forward text (descriptions usually follow images)
                            context = " ".join(forward_text)
                        else:
                            # Fallback: look backward at last 300 chars
                            context = all_text[-300:].strip()

                    mapping[embed_id] = context

                all_text += para_text + "\n"

            # Resolve relationship IDs to image filenames
            resolved = {}
            try:
                rels_content = zf.read("word/_rels/document.xml.rels")
                rels_root = ET.fromstring(rels_content)
                ns = "http://schemas.openxmlformats.org/package/2006/relationships"

                for rel in rels_root.iter(f"{{{ns}}}Relationship"):
                    rid = rel.get("Id", "")
                    target = rel.get("Target", "")
                    if rid in mapping and "media/" in target:
                        image_name = os.path.splitext(os.path.basename(target))[0]
                        resolved[image_name] = mapping[rid]
            except Exception:
                pass

            return resolved

        except Exception as e:
            logger.error(f"Failed to build image paragraph map: {e}")
            return {}

    def _get_paragraph_texts(self, zf: zipfile.ZipFile) -> dict[str, str]:
        """Fallback: build a simple image_name → relationship_id map."""
        try:
            rels_content = zf.read("word/_rels/document.xml.rels")
            root = ET.fromstring(rels_content)
            ns = "http://schemas.openxmlformats.org/package/2006/relationships"

            image_rels = {}
            for rel in root.iter(f"{{{ns}}}Relationship"):
                target = rel.get("Target", "")
                rid = rel.get("Id", "")
                if "media/" in target:
                    image_name = os.path.splitext(os.path.basename(target))[0]
                    image_rels[rid] = image_name
            return {v: k for k, v in image_rels.items()}
        except Exception:
            return {}

    def _describe_with_vision(self, image_path: str, surrounding_text: str) -> str:
        """Use a Vision LLM to generate a rich description of the image."""
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Determine MIME type
            ext = os.path.splitext(image_path)[1].lower()
            mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".gif": "image/gif", ".webp": "image/webp"}
            mime_type = mime_map.get(ext, "image/png")

            llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model_name=VISION_MODEL,
                temperature=0.1,
                max_tokens=512,
            )

            prompt_text = IMAGE_DESCRIPTION_PROMPT.format(
                surrounding_text=surrounding_text[:300] if surrounding_text else "No surrounding text available."
            )

            message = HumanMessage(content=[
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
            ])

            response = llm.invoke([message])
            description = response.content.strip()
            logger.info(f"Vision description for {os.path.basename(image_path)}: {description[:100]}...")
            return description

        except Exception as e:
            logger.warning(f"Vision LLM failed for {image_path}: {e}")
            return ""

    def _guess_section(self, text: str) -> str:
        if not text:
            return "Unknown"
        section_patterns = [
            (r"figure\s*\d+", "Figures"),
            (r"fig\.\s*\d+", "Figures"),
            (r"table\s*\d+", "Tables"),
            (r"result", "Results"),
            (r"claim", "Claims"),
            (r"example", "Examples"),
            (r"graph", "Graphs"),
            (r"chart", "Charts"),
            (r"spectrum", "Analysis"),
            (r"reflectiv", "Performance"),
            (r"transmission", "Performance"),
        ]
        text_lower = text.lower()
        for pattern, section in section_patterns:
            if re.search(pattern, text_lower):
                return section
        return "General"
