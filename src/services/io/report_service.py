import os
import webbrowser
from datetime import datetime


class ReportService:
    @staticmethod
    def generate_computation_report(client_data, tax_data, output_path):
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; padding: 40px; }}
                .header {{ border-bottom: 2px solid #006ADC; padding-bottom: 10px; margin-bottom: 30px; }}
                .brand {{ color: #006ADC; font-size: 24px; font-weight: bold; }}
                .client-info {{ margin-bottom: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .section {{ margin-bottom: 40px; }}
                .section-title {{ background: #f4f7f9; padding: 8px 15px; font-weight: bold; border-left: 4px solid #006ADC; margin-bottom: 15px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .label {{ color: #666; }}
                .value {{ text-align: right; font-weight: bold; }}
                .total-row {{ background: #f9f9f9; font-weight: bold; font-size: 1.1em; }}
                .footer {{ margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; font-size: 0.9em; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="brand">EMERALD ITR PRO</div>
                <div>TAX COMPUTATION STATEMENT - AY 2026-27</div>
            </div>
            
            <div class="client-info">
                <div>
                    <div class="label">Taxpayer Name</div>
                    <div style="font-size: 1.2em; font-weight: bold;">{client_data.get('name', 'N/A')}</div>
                </div>
                <div>
                    <div class="label">Permanent Account Number (PAN)</div>
                    <div style="font-size: 1.2em; font-weight: bold; color: #006ADC;">{client_data.get('pan', 'N/A')}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">PART B - COMPUTATION OF TOTAL INCOME</div>
                <table>
                    <tr><td class="label">1. Income from Salary</td><td class="value">₹ {int(tax_data.get('sal', 0)):,}</td></tr>
                    <tr><td class="label">2. Income from House Property</td><td class="value">₹ {int(tax_data.get('hp_total', 0)):,}</td></tr>
                    <tr><td class="label">3. Profits from Business or Profession</td><td class="value">₹ {int(tax_data.get('bp_total', 0)):,}</td></tr>
                    <tr><td class="label">4. Capital Gains</td><td class="value">₹ {int(tax_data.get('stcg_sum', 0) + tax_data.get('ltcg_112a_sum', 0)):,}</td></tr>
                    <tr><td class="label">5. Income from Other Sources</td><td class="value">₹ {int(tax_data.get('os_total', 0)):,}</td></tr>
                    <tr class="total-row"><td class="label">GROSS TOTAL INCOME (GTI)</td><td class="value">₹ {int(tax_data.get('gti', 0)):,}</td></tr>
                    <tr><td class="label">6. Less: Deductions under Chapter VI-A</td><td class="value">₹ {int(tax_data.get('ded_total', 0)):,}</td></tr>
                    <tr class="total-row" style="background: #eef6ff;"><td class="label">TOTAL TAXABLE INCOME (TTI)</td><td class="value">₹ {int(tax_data.get('tti', 0)):,}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">PART C - COMPUTATION OF TAX LIABILITY</div>
                <table>
                    <tr><td class="label">Tax on Total Income (at Slab Rates)</td><td class="value">₹ {int(tax_data.get('slab_tax', 0)):,}</td></tr>
                    <tr><td class="label">Add: Surcharge</td><td class="value">₹ {int(tax_data.get('surcharge', 0)):,}</td></tr>
                    <tr><td class="label">Add: Health & Education Cess @ 4%</td><td class="value">₹ {int(tax_data.get('cess', 0)):,}</td></tr>
                    <tr class="total-row"><td class="label">TOTAL TAX, SURCHARGE & CESS</td><td class="value">₹ {int(tax_data.get('tax_total', 0)):,}</td></tr>
                    <tr><td class="label">Less: Tax Credits (TDS/TCS/Advance Tax)</td><td class="value">₹ {int(tax_data.get('it_total', 0)):,}</td></tr>
                    <tr class="total-row" style="background: #fff8f0; border-top: 2px solid #f59e0b;">
                        <td class="label">NET TAX PAYABLE / (REFUND)</td>
                        <td class="value" style="color: #d32f2f;">₹ {int(tax_data.get('due_tax', 0) - tax_data.get('it_total', 0)):,}</td>
                    </tr>
                </table>
            </div>

            <div class="footer">
                This is a computer-generated statement prepared using Emerald ITR Pro. Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            </div>
        </body>
        </html>
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        webbrowser.open("file://" + os.path.abspath(output_path))
