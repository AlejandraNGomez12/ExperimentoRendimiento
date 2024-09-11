import json
from uuid import uuid4
from fastapi import APIRouter, Depends, status,HTTPException
from sqlmodel import Session, text, delete
from fastapi.responses import PlainTextResponse
from uuid import uuid4
from ..dependencies import get_session
from ..entities.report import Report
import boto3
import os

os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''

sqs_client = boto3.client('sqs', region_name='us-east-2')

SQS_QUEUE_URL = 'https://sqs.us-east-2.amazonaws.com/509399610552/QueueEmail'

router = APIRouter(prefix="/reports")

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Report)
async def create(*, session: Session = Depends(get_session), report: Report):
    print(report)
    
    report_db = Report(**report.model_dump())
    report_db.id = uuid4()

    message = {
        "id": str(report_db.id),
        "email": report_db.email,
        "filtro": report_db.filters,
        "type": report_db.type
    }
    try:
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        
        report_db.menssageId = response['MessageId']
        session.add(report_db)
        session.commit()
        session.refresh(report_db)
        
        print(response)
        return report_db
    
    except Exception as e:
        session.rollback()
        print(f"Error enviando mensaje a SQS: {e}")
        raise HTTPException(status_code=500, detail="Error enviando mensaje a la cola SQS.")

@router.get("/ping", status_code=status.HTTP_200_OK, response_class=PlainTextResponse)
async def ping(*, session: Session = Depends(get_session)):
    session.exec(text("SELECT 1"))
    return "PONG"

@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset(*, session: Session = Depends(get_session)):
    session.exec(delete(Report))
    session.commit()
    return {"msg": "Todos los datos fueron eliminados"}