import pytest
from httpx import AsyncClient

from tests.conftest import login, payload


@pytest.mark.asyncio
async def test_create_and_repeat_reason_not_merged(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    first = await client.post("/api/stoppages", json=payload(client, duration_minutes=10), headers=headers)
    second = await client.post("/api/stoppages", json=payload(client, duration_minutes=15), headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    listing = await client.get("/api/stoppages?search=P-05", headers=headers)
    assert listing.json()["pagination"]["total"] == 2
    summary = await client.get(
        "/api/dashboard/summary?date_from=2026-08-28&date_to=2026-08-28&machine_id=" + str(client.machine5.id),
        headers=headers,
    )
    assert float(summary.json()["kpis"]["total_downtime_minutes"]) == 25


@pytest.mark.asyncio
async def test_shift_c_keeps_production_date(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post("/api/stoppages", json=payload(client, duration_minutes=12), headers=headers)
    assert created.status_code == 201
    assert created.json()["production_date"] == "2026-08-28"
    assert created.json()["shift"]["code"] == "C"


@pytest.mark.asyncio
async def test_multiple_machines_summary(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    for machine, minutes in [
        (client.machine1, 20),
        (client.machine2, 30),
        (client.machine3, 50),
    ]:
        response = await client.post(
            "/api/stoppages",
            json=payload(client, machine_id=str(machine.id), duration_minutes=minutes),
            headers=headers,
        )
        assert response.status_code == 201
    summary = await client.get("/api/dashboard/summary?date_from=2026-08-28&date_to=2026-08-28", headers=headers)
    by_code = {row["name"]: float(row["downtime_minutes"]) for row in summary.json()["machines"]}
    assert by_code["P-01"] == 20
    assert by_code["P-02"] == 30
    assert by_code["P-03"] == 50


@pytest.mark.asyncio
async def test_validation_duration(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/stoppages", json=payload(client, duration_minutes=0), headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_supervisor_cannot_edit_other_records(client: AsyncClient):
    admin = await login(client, "admin", "AdminPass123!")
    created = await client.post(
        "/api/stoppages",
        json=payload(client, supervisor_id=str(client.sup_b.id), duration_minutes=10),
        headers={"Authorization": f"Bearer {admin}"},
    )
    record_id = created.json()["id"]
    super_a = await login(client, "supera", "SuperPass123!")
    denied = await client.patch(
        f"/api/stoppages/{record_id}",
        json={"duration_minutes": 20},
        headers={"Authorization": f"Bearer {super_a}"},
    )
    assert denied.status_code == 403
    super_b = await login(client, "superb", "SuperPass123!")
    allowed = await client.patch(
        f"/api/stoppages/{record_id}",
        json={"duration_minutes": 20},
        headers={"Authorization": f"Bearer {super_b}"},
    )
    assert allowed.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_creates_persist_both(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    async def create(minutes: int):
        return await client.post("/api/stoppages", json=payload(client, duration_minutes=minutes), headers=headers)

    first = await create(11)
    second = await create(13)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


@pytest.mark.asyncio
async def test_soft_delete_hides_record(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post("/api/stoppages", json=payload(client, duration_minutes=9), headers=headers)
    record_id = created.json()["id"]
    deleted = await client.delete(f"/api/stoppages/{record_id}", headers=headers)
    assert deleted.status_code == 204
    listing = await client.get("/api/stoppages", headers=headers)
    ids = [row["id"] for row in listing.json()["data"]]
    assert record_id not in ids


@pytest.mark.asyncio
async def test_excel_and_pdf_generation(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/stoppages", json=payload(client, duration_minutes=18), headers=headers)
    excel = await client.get("/api/reports/excel?date_from=2026-08-28&date_to=2026-08-28&report_type=complete", headers=headers)
    assert excel.status_code == 200
    assert excel.headers["content-type"].startswith("application/vnd.openxmlformats")
    pdf = await client.get("/api/reports/pdf?date_from=2026-08-28&date_to=2026-08-28", headers=headers)
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_empty_export_is_not_misleading(client: AsyncClient):
    token = await login(client, "admin", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    excel = await client.get("/api/reports/excel?date_from=2020-01-01&date_to=2020-01-02", headers=headers)
    assert excel.status_code == 404
    assert "No records found" in excel.json()["error"]["message"]
