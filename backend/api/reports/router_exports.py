from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from backend.core.database import get_session
from backend.api.auth.deps import get_current_user
from backend.models.models import Usuario, LibroTransacciones
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/export", tags=["Exports"])

@router.get("/transactions/excel")
async def export_transactions_excel(
    limit: Optional[int] = 1000,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Export transaction history to Excel"""
    try:
        statement = select(LibroTransacciones).where(
            LibroTransacciones.id_usuario == current_user.id_usuario
        ).limit(limit)
        results = session.exec(statement).all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No hay transacciones para exportar")

        # Convert to DataFrame
        data = []
        for t in results:
            data.append({
                "ID": t.id_transaccion,
                "Fecha": t.fecha.strftime("%Y-%m-%d") if t.fecha else "",
                "Monto": t.monto,
                "Descripción": t.descripcion,
                "Referencia": t.referencia
            })
            
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Transacciones')
            
        output.seek(0)
        
        headers = {
            'Content-Disposition': f'attachment; filename="transacciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        }
        return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions/pdf")
async def export_transactions_pdf(
    limit: Optional[int] = 500,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Export transaction history to PDF"""
    try:
        statement = select(LibroTransacciones).where(
            LibroTransacciones.id_usuario == current_user.id_usuario
        ).limit(limit)
        results = session.exec(statement).all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No hay transacciones para exportar")

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, "Historial de Transacciones - FuturoForbes")
        p.setFont("Helvetica", 10)
        p.drawString(100, height - 70, f"Usuario: {current_user.login}")
        p.drawString(100, height - 85, f"Fecha Reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y = height - 120
        p.setFont("Helvetica-Bold", 10)
        p.drawString(100, y, "Fecha")
        p.drawString(180, y, "Monto")
        p.drawString(260, y, "Descripción")
        
        p.line(100, y - 5, 500, y - 5)
        
        y -= 20
        p.setFont("Helvetica", 9)
        for t in results:
            if y < 50:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica", 9)
            
            p.drawString(100, y, t.fecha.strftime("%Y-%m-%d") if t.fecha else "")
            p.drawString(180, y, f"${t.monto:,.2f}")
            p.drawString(260, y, (t.descripcion[:40] + '..') if t.descripcion and len(t.descripcion) > 40 else (t.descripcion or ""))
            y -= 15
            
        p.showPage()
        p.save()
        
        buffer.seek(0)
        headers = {
            'Content-Disposition': f'attachment; filename="transacciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        }
        return StreamingResponse(buffer, headers=headers, media_type='application/pdf')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
