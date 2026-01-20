import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from backend.config import OPENAI_API_KEY, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD
from openai import OpenAI

def generate_report_with_ai(leads: List[Dict]) -> str:
    """
    Genera un reporte destacado usando OpenAI.
    Filtra los leads más relevantes y genera resumen.
    """
    if not OPENAI_API_KEY:
        return "Error: OpenAI API Key no configurada"
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Preparar datos para el prompt
    leads_summary = []
    for lead in leads[:50]:  # Limitar a 50 leads para no exceder tokens
        summary = f"- {lead.get('project_name', 'Sin nombre')} ({lead.get('source', '')}): {lead.get('description', '')[:100]}"
        leads_summary.append(summary)
    
    leads_text = "\n".join(leads_summary)
    
    prompt = f"""
Analiza los siguientes leads de proyectos y genera un reporte ejecutivo destacando los más relevantes.

Criterios de relevancia:
- Proyectos nuevos o recientes
- Alta inversión o impacto económico
- Sectores estratégicos (energía, infraestructura, tecnología, minería)
- Oportunidades de financiamiento o M&A

Leads encontrados:
{leads_text}

Genera un reporte en formato texto con:
1. Resumen ejecutivo (2-3 líneas)
2. Top 5 leads más relevantes con justificación
3. Análisis por sector
4. Recomendaciones de seguimiento

Formato el reporte de manera profesional y concisa.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un analista experto en identificar oportunidades de proyectos, financiamiento y M&A."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        report = response.choices[0].message.content
        return report
    except Exception as e:
        return f"Error al generar reporte con IA: {str(e)}"

def send_email_report(report: str, to_email: str) -> bool:
    """
    Envía reporte por email usando SMTP.
    """
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        return False
    
    try:
        # Configurar servidor SMTP (Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Reporte de Leads - Master Scraper"
        
        msg.attach(MIMEText(report, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False

