from pathlib import Path
from datetime import datetime
from fpdf import FPDF

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from config import PDF_TITLE, PDF_SUBTITLE, PDF_COLORS


class PatentReportPDF(FPDF):

    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(59, 130, 246)
        self.cell(0, 8, PDF_TITLE, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="L")
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.ln(5)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_text(self, text: str):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)


class ReportGenerator:

    def generate(
        self,
        features: list[dict],
        validation: list[dict],
        mapping: dict[str, dict],
        prior_art_labels: dict[str, str],
        output_path: str | Path,
        title: str = "",
        inventors: str = "",
    ) -> str:
        pdf = PatentReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        self._add_overview(pdf, title, inventors)
        self._add_features_table(pdf, features)
        pdf.add_page()
        self._add_validation_table(pdf, validation)
        pdf.add_page()
        self._add_mapping_matrix(pdf, features, mapping, prior_art_labels)
        pdf.add_page()
        self._add_gap_analysis(pdf, features, mapping, prior_art_labels)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))
        return str(output_path)

    def _add_overview(self, pdf: PatentReportPDF, title: str, inventors: str):
        pdf.section_title("1. Invention Overview")
        pdf.add_text(f"Title: {title or 'N/A'}")
        pdf.add_text(f"Inventors: {inventors or 'N/A'}")
        pdf.add_text(f"Report Type: IDF vs PR Key Features Correlation Analysis")

    def _add_features_table(self, pdf: PatentReportPDF, features: list[dict]):
        pdf.section_title("2. Key Features Extracted from IDF")

        col_widths = [15, 50, 150, 50]
        headers = ["#", "Feature", "Description", "IDF Section"]

        pdf.set_font("Helvetica", "B", 8)
        r, g, b = PDF_COLORS["header"]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 7, header, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(30, 30, 30)
        for idx, f in enumerate(features):
            fill = idx % 2 == 0
            if fill:
                pdf.set_fill_color(240, 240, 245)
            else:
                pdf.set_fill_color(255, 255, 255)

            row_data = [
                f.get("id", f"KF{idx+1}"),
                f.get("name", ""),
                f.get("description", "")[:120],
                f.get("idf_section", ""),
            ]

            max_h = 6
            for i, val in enumerate(row_data):
                pdf.cell(col_widths[i], max_h, val, border=1, fill=fill)
            pdf.ln()

    def _add_validation_table(self, pdf: PatentReportPDF, validation: list[dict]):
        pdf.section_title("3. PR Coverage Validation")

        col_widths = [15, 60, 30, 25, 135]
        headers = ["#", "Feature", "PR Element", "Captured", "Details"]

        pdf.set_font("Helvetica", "B", 8)
        r, g, b = PDF_COLORS["header"]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 7, header, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(30, 30, 30)
        for idx, v in enumerate(validation):
            captured = v.get("captured", False)
            if captured:
                pdf.set_fill_color(220, 252, 231)
            else:
                pdf.set_fill_color(254, 226, 226)

            row = [
                v.get("feature_id", ""),
                v.get("feature_name", "")[:45],
                v.get("pr_element", "N/A"),
                "Yes" if captured else "No",
                v.get("details", "")[:100],
            ]
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 6, val, border=1, fill=True)
            pdf.ln()

    def _add_mapping_matrix(
        self,
        pdf: PatentReportPDF,
        features: list[dict],
        mapping: dict[str, dict],
        prior_art_labels: dict[str, str],
    ):
        pdf.section_title("4. Key Feature to Prior Art Mapping Matrix")

        prior_art_ids = sorted(prior_art_labels.keys()) if prior_art_labels else sorted(
            set(k for m in mapping.values() for k in m.keys())
        )

        if not prior_art_ids:
            pdf.add_text("No prior art mapping data available.")
            return

        num_pa = len(prior_art_ids)
        feature_col_w = 55
        pa_col_w = min(45, (pdf.w - 20 - feature_col_w) / max(num_pa, 1))

        pdf.set_font("Helvetica", "B", 7)
        r, g, b = PDF_COLORS["header"]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(feature_col_w, 7, "Key Feature", border=1, fill=True, align="C")
        for pa_id in prior_art_ids:
            label = prior_art_labels.get(pa_id, pa_id)[:25]
            pdf.cell(pa_col_w, 7, f"{pa_id}: {label}", border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 6)
        for f in features:
            fid = f.get("id", "")
            fname = f.get("name", "")
            feature_mapping = mapping.get(fid, {})

            pdf.set_text_color(30, 30, 30)
            pdf.set_fill_color(245, 245, 250)
            pdf.cell(feature_col_w, 12, f"{fid}: {fname}"[:40], border=1, fill=True)

            for pa_id in prior_art_ids:
                value = feature_mapping.get(pa_id, "N/A")
                if value == "NO":
                    pdf.set_fill_color(*PDF_COLORS["novel"])
                    pdf.set_text_color(255, 255, 255)
                elif value.startswith("Yes, Partially"):
                    pdf.set_fill_color(*PDF_COLORS["partial"])
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.set_fill_color(255, 255, 255)
                    pdf.set_text_color(30, 30, 30)

                display_val = value[:35] + "..." if len(value) > 35 else value
                pdf.cell(pa_col_w, 12, display_val, border=1, fill=True)
                pdf.set_text_color(30, 30, 30)

            pdf.ln()

    def _add_gap_analysis(
        self,
        pdf: PatentReportPDF,
        features: list[dict],
        mapping: dict[str, dict],
        prior_art_labels: dict[str, str],
    ):
        pdf.section_title("5. Gap Analysis - Novel Features")

        novel_features = []
        partial_features = []

        for f in features:
            fid = f.get("id", "")
            f_mapping = mapping.get(fid, {})
            all_no = all(v == "NO" for v in f_mapping.values()) if f_mapping else False
            any_partial = any("Partially" in str(v) for v in f_mapping.values())

            if all_no:
                novel_features.append(f)
            elif any_partial:
                partial_features.append(f)

        if novel_features:
            pdf.add_text("Features NOT found in ANY prior art (completely novel):")
            for f in novel_features:
                pdf.add_text(f"  - {f.get('id', '')}: {f.get('name', '')}")

        if partial_features:
            pdf.ln(3)
            pdf.add_text("Features only partially covered by prior art:")
            for f in partial_features:
                pdf.add_text(f"  - {f.get('id', '')}: {f.get('name', '')}")

        pdf.section_title("6. Summary")
        total = len(features)
        novel = len(novel_features)
        pdf.add_text(f"Total key features identified: {total}")
        pdf.add_text(f"Completely novel features: {novel}")
        pdf.add_text(f"Features with partial prior art: {len(partial_features)}")
        pdf.add_text(f"Features with full prior art coverage: {total - novel - len(partial_features)}")
