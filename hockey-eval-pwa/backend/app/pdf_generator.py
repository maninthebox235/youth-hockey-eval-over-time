from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

def generate_player_evaluation_pdf(player, evaluations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
    )
    
    story.append(Paragraph(f"Player Evaluation Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    player_info = [
        ['Player Name:', player.name],
        ['Jersey Number:', str(player.jersey_number) if player.jersey_number else 'N/A'],
        ['Position:', player.position or 'N/A'],
        ['Age Group:', player.age_group or 'N/A'],
        ['Report Date:', datetime.now().strftime('%Y-%m-%d')],
    ]
    
    player_table = Table(player_info, colWidths=[2*inch, 4*inch])
    player_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(player_table)
    story.append(Spacer(1, 0.3*inch))
    
    if evaluations:
        story.append(Paragraph("Evaluation History", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        for eval in evaluations[-5:]:
            story.append(Paragraph(f"Date: {eval.date.strftime('%Y-%m-%d')} | Type: {eval.evaluation_type}", styles['Heading3']))
            story.append(Paragraph(f"Evaluator: {eval.evaluator_name}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            skills_data = [
                ['Skill', 'Rating'],
                ['Skating', str(eval.skating)],
                ['Shooting', str(eval.shooting)],
                ['Passing', str(eval.passing)],
                ['Puck Handling', str(eval.puck_handling)],
                ['Hockey IQ', str(eval.hockey_iq)],
                ['Physicality', str(eval.physicality)],
            ]
            
            skills_table = Table(skills_data, colWidths=[3*inch, 1*inch])
            skills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(skills_table)
            story.append(Spacer(1, 0.1*inch))
            
            if eval.strengths:
                story.append(Paragraph(f"<b>Strengths:</b> {eval.strengths}", styles['Normal']))
            if eval.areas_for_improvement:
                story.append(Paragraph(f"<b>Areas for Improvement:</b> {eval.areas_for_improvement}", styles['Normal']))
            if eval.notes:
                story.append(Paragraph(f"<b>Notes:</b> {eval.notes}", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
    else:
        story.append(Paragraph("No evaluations recorded yet.", styles['Normal']))
    
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
