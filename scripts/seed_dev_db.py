#!/usr/bin/env python3
"""Seed a small set of DB rows for local development and tests.

Creates: an admin user, one vendor, one matter, one invoice and one line item.
"""
import sys
import os
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from db.database import get_db_session, init_db
from models.db_models import User, Vendor, Matter, Invoice, LineItem


def seed():
    init_db()
    session = get_db_session()
    try:
        # Simple idempotent checks
        admin = session.query(User).filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                password_hash='dev-only',
                role='admin',
                active=True,
            )
            session.add(admin)

        vendor = session.query(Vendor).filter_by(external_id='v-001').first()
        if not vendor:
            vendor = Vendor(
                external_id='v-001',
                name='Test Vendor',
                total_spend=1000.0,
                invoice_count=1,
                avg_rate=200.0,
                status='Active',
            )
            session.add(vendor)

        matter = session.query(Matter).filter_by(name='Test Matter').first()
        if not matter:
            matter = Matter(
                name='Test Matter',
                category='General',
                priority='Low',
            )
            session.add(matter)

        session.flush()  # assign ids

        invoice = session.query(Invoice).filter_by(invoice_number='INV-0001').first()
        if not invoice:
            invoice = Invoice(
                invoice_number='INV-0001',
                vendor_id=vendor.id,
                matter_id=matter.id,
                amount=1000.0,
                total_amount=1000.0,
                date=datetime.utcnow(),
                status='processed',
                description='Seed invoice for dev',
                uploaded_by=admin.id,
                processed=True,
            )
            session.add(invoice)

        session.flush()

        li = session.query(LineItem).filter_by(invoice_id=invoice.id).first()
        if not li:
            li = LineItem(
                invoice_id=invoice.id,
                description='Seed line',
                hours=5.0,
                rate=200.0,
                amount=1000.0,
                timekeeper='TK1',
            )
            session.add(li)

        session.commit()
        print('Seeded dev DB: admin, vendor, matter, invoice, line item')
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    seed()
