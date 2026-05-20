from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base
from app.models import (
    Category,
    City,
    ClientProfile,
    LeadClick,
    Partner,
    PartnerOffer,
    PartnerPhoto,
    PartnerQrLink,
    PaymentReceipt,
    PaymentRequest,
    PrivilegeVerificationSession,
    PrivilegeVerificationStatus,
    Subscription,
    User,
    VkLinkCode,
    UserRole,
)


def _literal_assignment(module: ast.Module, name: str) -> str | None:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    return value
    return None


def test_migration_files_have_single_head_revision() -> None:
    revisions: dict[str, str | None] = {}
    for path in Path("alembic/versions").glob("*.py"):
        module = ast.parse(path.read_text())
        revision = _literal_assignment(module, "revision")
        down_revision = _literal_assignment(module, "down_revision")
        assert revision is not None
        revisions[revision] = down_revision

    referenced_revisions = {down_revision for down_revision in revisions.values() if down_revision}
    heads = sorted(set(revisions) - referenced_revisions)

    assert heads == ["20260520_0010"]


def test_base_metadata_includes_domain_foundation_tables() -> None:
    assert {
        "users",
        "cities",
        "client_profiles",
        "partners",
        "partner_offers",
        "partner_photos",
        "payment_requests",
        "payment_receipts",
        "subscriptions",
        "partner_qr_links",
        "lead_clicks",
        "privilege_verification_sessions",
        "admin_users",
        "vk_link_codes",
        "categories",
        "client_password_setup_tokens",
    }.issubset(Base.metadata.tables)


def test_privilege_verification_model_has_single_metadata_table_and_mapper() -> None:
    table_name = "privilege_verification_sessions"

    assert list(Base.metadata.tables).count(table_name) == 1
    assert [
        mapper.class_
        for mapper in Base.registry.mappers
        if mapper.local_table.name == table_name
    ] == [PrivilegeVerificationSession]


def test_verify_module_remains_backward_compatible_alias() -> None:
    from app.models.verify import (
        PrivilegeVerificationSession as VerifyPrivilegeVerificationSession,
        PrivilegeVerificationStatus as VerifyPrivilegeVerificationStatus,
    )

    assert VerifyPrivilegeVerificationSession is PrivilegeVerificationSession
    assert VerifyPrivilegeVerificationStatus is PrivilegeVerificationStatus


def test_domain_foundation_persists_in_sqlite_memory() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    Base.metadata.create_all(bind=engine)
    now = datetime.now(timezone.utc)

    try:
        with session_factory() as session:
            _create_domain_foundation_graph(session, now)

        with session_factory() as session:
            assert session.query(City).count() == 2
            assert session.query(User).count() == 2
            assert session.query(ClientProfile).count() == 1
            assert session.query(Partner).count() == 1
            assert session.query(PartnerOffer).count() == 1
            assert session.query(PartnerPhoto).count() == 1
            assert session.query(PartnerQrLink).count() == 1
            assert session.query(LeadClick).count() == 1
            assert session.query(PaymentRequest).count() == 1
            assert session.query(PaymentReceipt).count() == 1
            assert session.query(Subscription).count() == 1
            assert session.query(PrivilegeVerificationSession).count() == 1
            assert session.query(VkLinkCode).count() == 1
    finally:
        engine.dispose()


def _create_domain_foundation_graph(session: Session, now: datetime) -> None:
    novosibirsk = City(name="Новосибирск", slug="novosibirsk", sort_order=10)
    cherepovets = City(name="Череповец", slug="cherepovets", sort_order=20)
    partner_user = User(email="partner@example.com", role=UserRole.PARTNER.value)
    client_user = User(email="client@example.com", role=UserRole.CLIENT.value)
    session.add_all([novosibirsk, cherepovets, partner_user, client_user])
    session.flush()

    client = ClientProfile(
        user_id=client_user.id,
        selected_city_id=novosibirsk.id,
        full_name="Client Example",
        vk_user_id="vk-client-1",
        source="test",
    )
    partner = Partner(
        city_id=novosibirsk.id,
        owner_user_id=partner_user.id,
        category_slug="beauty",
        name="Beauty Partner",
        is_verified=True,
    )
    session.add_all([client, partner])
    session.flush()

    offer = PartnerOffer(
        partner_id=partner.id,
        title="Club privilege",
        benefit_text="10% discount",
        base_price=Decimal("1000.00"),
        discount_percent=Decimal("10.00"),
    )
    photo = PartnerPhoto(partner_id=partner.id, url="/uploads/partners/1/photos/photo-test.webp", alt_text="Gallery")
    qr_link = PartnerQrLink(partner_id=partner.id, slug="beauty-partner", target_url="https://example.com")
    session.add_all([offer, photo, qr_link])
    session.flush()

    lead_click = LeadClick(
        partner_id=partner.id,
        qr_link_id=qr_link.id,
        city_id=novosibirsk.id,
        source="qr",
        session_id="session-1",
    )
    payment_request = PaymentRequest(client_id=client.id, amount=Decimal("2990.00"), source="manual")
    session.add_all([lead_click, payment_request])
    session.flush()

    receipt = PaymentReceipt(payment_request_id=payment_request.id, file_url="https://example.com/receipt.jpg")
    subscription = Subscription(
        client_id=client.id,
        starts_at=now,
        ends_at=now + timedelta(days=30),
        source_payment_request_id=payment_request.id,
    )
    verification_session = PrivilegeVerificationSession(
        client_id=client.id,
        partner_id=partner.id,
        offer_id=offer.id,
        code="ABC123",
        expires_at=now + timedelta(minutes=10),
    )
    vk_link_code = VkLinkCode(
        client_id=client.id,
        code="VK123456",
        expires_at=now + timedelta(minutes=10),
    )
    session.add_all([receipt, subscription, verification_session, vk_link_code])
    session.commit()
