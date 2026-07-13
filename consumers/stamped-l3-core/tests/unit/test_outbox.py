from stamped_l3_core.outbox import TransactionalOutbox


def test_outbox_stages_and_publishes():
    outbox = TransactionalOutbox()
    finding = {"finding_id": "f-1", "category": "md_overlap", "dedupe_key": "sha256:abc"}
    outbox.stage(finding)
    assert len(outbox.pending) == 1
    published = outbox.publish()
    assert published == [finding]
    assert outbox.pending == []
    assert outbox.published == [finding]


def test_outbox_accumulates_published():
    outbox = TransactionalOutbox()
    outbox.stage({"finding_id": "f-1"})
    outbox.publish()
    outbox.stage({"finding_id": "f-2"})
    outbox.publish()
    assert len(outbox.published) == 2
