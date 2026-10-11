from backend.credence_gov.architecture import ArchitecturePlan, ModuleBoundary, Plane


def test_architecture_plan_defines_distinct_planes() -> None:
    plan = ArchitecturePlan(
        name="CredenceAI-Gov",
        planes=[
            Plane.CONTROL,
            Plane.EVIDENCE,
            Plane.REVIEW,
            Plane.INTELLIGENCE,
        ],
    )

    assert plan.name == "CredenceAI-Gov"
    assert set(plan.plane_names()) == {"control", "evidence", "review", "intelligence"}
    assert plan.has_plane(Plane.EVIDENCE) is True


def test_module_boundaries_keep_decisions_out_of_workers() -> None:
    boundary = ModuleBoundary(
        module_name="cases.service",
        plane=Plane.CONTROL,
        may_write_decisions=True,
        may_write_artifacts=False,
    )

    worker = ModuleBoundary(
        module_name="workers.celery_app",
        plane=Plane.INTELLIGENCE,
        may_write_decisions=False,
        may_write_artifacts=False,
    )

    assert boundary.is_control_plane is True
    assert worker.can_write_decisions is False
    assert worker.can_write_artifacts is False
