"""
Idempotent synchronization service from PostgreSQL to Neo4j.
"""
import logging
from apps.cases.models import Case, Party, CaseParty, CaseJudge, CaseCitation
from apps.courts.models import Court, Judge
from apps.legal.models import Act, Section, CaseSection
from apps.documents.models import Document
from .connection import get_neo4j_driver, check_neo4j_connection

logger = logging.getLogger(__name__)


def sync_knowledge_graph(dry_run=False, case_id=None):
    """
    Synchronizes cases and related entities from PostgreSQL to Neo4j using MERGE statements.
    If dry_run=True, counts records and queries without executing writes.
    Returns a dictionary of sync statistics.
    """
    stats = {
        "cases_synced": 0,
        "courts_synced": 0,
        "judges_synced": 0,
        "parties_synced": 0,
        "documents_synced": 0,
        "acts_synced": 0,
        "sections_synced": 0,
        "relationships_created": 0,
        "dry_run": dry_run,
        "neo4j_connected": False,
    }

    connected, message = check_neo4j_connection()
    stats["neo4j_connected"] = connected
    stats["connection_message"] = message

    if not connected and not dry_run:
        logger.warning(f"Neo4j is not reachable: {message}. Sync cannot execute writes.")
        return stats

    driver = get_neo4j_driver() if connected else None

    # Determine querysets
    case_qs = Case.objects.select_related("court")
    if case_id:
        case_qs = case_qs.filter(pk=case_id)

    cases = list(case_qs)
    stats["cases_synced"] = len(cases)

    # Gather courts
    court_ids = {c.court_id for c in cases if c.court_id}
    courts = Court.objects.filter(id__in=court_ids)
    stats["courts_synced"] = courts.count()

    # Gather judges
    case_ids = [c.id for c in cases]
    case_judges = list(CaseJudge.objects.filter(case_id__in=case_ids).select_related("judge"))
    judge_ids = {cj.judge_id for cj in case_judges}
    judges = Judge.objects.filter(id__in=judge_ids)
    stats["judges_synced"] = judges.count()

    # Gather parties
    case_parties = list(CaseParty.objects.filter(case_id__in=case_ids).select_related("party"))
    party_ids = {cp.party_id for cp in case_parties}
    parties = Party.objects.filter(id__in=party_ids)
    stats["parties_synced"] = parties.count()

    # Gather documents
    documents = list(Document.objects.filter(case_id__in=case_ids))
    stats["documents_synced"] = len(documents)

    # Gather citations
    citations = list(CaseCitation.objects.filter(source_case_id__in=case_ids))

    # Gather legal sections
    case_sections = list(CaseSection.objects.filter(case_id__in=case_ids).select_related("section", "section__act"))
    section_ids = {cs.section_id for cs in case_sections}
    sections = Section.objects.filter(id__in=section_ids)
    stats["sections_synced"] = sections.count()
    act_ids = {s.act_id for s in sections if s.act_id}
    acts = Act.objects.filter(id__in=act_ids)
    stats["acts_synced"] = acts.count()

    stats["relationships_created"] = (
        len(cases) + # FILED_IN
        len(case_judges) + # HEARD_BY
        len(case_parties) + # HAS_PARTY
        len(documents) + # HAS_DOCUMENT
        len(citations) + # CITES
        len(case_sections) + # REFERENCES_SECTION
        len(act_ids) # PART_OF / REFERENCES_ACT
    )

    if dry_run or not connected:
        return stats

    # Execute MERGE queries in a transaction
    with driver.session() as session:
        # 1. Sync Courts
        for court in courts:
            session.run(
                """
                MERGE (co:Court {postgres_id: $postgres_id})
                SET co.name = $name,
                    co.court_type = $court_type
                """,
                postgres_id=court.id,
                name=court.court_name,
                court_type=court.court_type or "OTHER",
            )

        # 2. Sync Judges
        for judge in judges:
            session.run(
                """
                MERGE (j:Judge {postgres_id: $postgres_id})
                SET j.name = $name,
                    j.designation = $designation
                """,
                postgres_id=judge.id,
                name=judge.name,
                designation=judge.designation or "",
            )

        # 3. Sync Parties
        for party in parties:
            session.run(
                """
                MERGE (p:Party {postgres_id: $postgres_id})
                SET p.name = $name,
                    p.party_type = $party_type
                """,
                postgres_id=party.id,
                name=party.name,
                party_type=party.party_type or "OTHER",
            )

        # 4. Sync Acts
        for act in acts:
            session.run(
                """
                MERGE (a:Act {postgres_id: $postgres_id})
                SET a.name = $name,
                    a.short_code = $short_code,
                    a.act_year = $act_year
                """,
                postgres_id=act.id,
                name=act.act_name,
                short_code=act.short_code or "",
                act_year=act.act_year or 0,
            )

        # 5. Sync Sections
        for sec in sections:
            session.run(
                """
                MERGE (s:Section {postgres_id: $postgres_id})
                SET s.section_number = $section_number,
                    s.title = $title
                """,
                postgres_id=sec.id,
                section_number=sec.section_number,
                title=sec.title or "",
            )
            if sec.act_id:
                session.run(
                    """
                    MATCH (s:Section {postgres_id: $sec_id})
                    MATCH (a:Act {postgres_id: $act_id})
                    MERGE (s)-[:PART_OF]->(a)
                    """,
                    sec_id=sec.id,
                    act_id=sec.act_id,
                )

        # 6. Sync Cases & Documents & Relationships
        for c in cases:
            session.run(
                """
                MERGE (case:Case {postgres_id: $postgres_id})
                SET case.case_number = $case_number,
                    case.title = $title,
                    case.decision_date = $decision_date,
                    case.status = $status,
                    case.cnr_number = $cnr_number
                """,
                postgres_id=c.id,
                case_number=c.case_number,
                title=c.case_title,
                decision_date=str(c.decision_date) if c.decision_date else "",
                status=c.status,
                cnr_number=c.cnr_number or "",
            )

            if c.court_id:
                session.run(
                    """
                    MATCH (case:Case {postgres_id: $case_id})
                    MATCH (co:Court {postgres_id: $court_id})
                    MERGE (case)-[:FILED_IN]->(co)
                    """,
                    case_id=c.id,
                    court_id=c.court_id,
                )

        for cj in case_judges:
            session.run(
                """
                MATCH (case:Case {postgres_id: $case_id})
                MATCH (j:Judge {postgres_id: $judge_id})
                MERGE (case)-[r:HEARD_BY]->(j)
                SET r.role = $role
                """,
                case_id=cj.case_id,
                judge_id=cj.judge_id,
                role=cj.role,
            )

        for cp in case_parties:
            session.run(
                """
                MATCH (case:Case {postgres_id: $case_id})
                MATCH (p:Party {postgres_id: $party_id})
                MERGE (case)-[r:HAS_PARTY]->(p)
                SET r.role = $role
                """,
                case_id=cp.case_id,
                party_id=cp.party_id,
                role=cp.role,
            )

        for doc in documents:
            session.run(
                """
                MERGE (d:Document {postgres_id: $postgres_id})
                SET d.title = $title,
                    d.document_type = $document_type
                """,
                postgres_id=doc.id,
                title=doc.title,
                document_type=doc.document_type,
            )
            session.run(
                """
                MATCH (case:Case {postgres_id: $case_id})
                MATCH (d:Document {postgres_id: $doc_id})
                MERGE (case)-[:HAS_DOCUMENT]->(d)
                """,
                case_id=doc.case_id,
                doc_id=doc.id,
            )

        for cite in citations:
            if cite.cited_case_id:
                session.run(
                    """
                    MATCH (c1:Case {postgres_id: $src_id})
                    MATCH (c2:Case {postgres_id: $cited_id})
                    MERGE (c1)-[r:CITES]->(c2)
                    SET r.citation_text = $citation_text
                    """,
                    src_id=cite.source_case_id,
                    cited_id=cite.cited_case_id,
                    citation_text=cite.citation_text,
                )

        for cs in case_sections:
            session.run(
                """
                MATCH (c:Case {postgres_id: $case_id})
                MATCH (s:Section {postgres_id: $sec_id})
                MERGE (c)-[:REFERENCES_SECTION]->(s)
                """,
                case_id=cs.case_id,
                sec_id=cs.section_id,
            )
            if cs.section and cs.section.act_id:
                session.run(
                    """
                    MATCH (c:Case {postgres_id: $case_id})
                    MATCH (a:Act {postgres_id: $act_id})
                    MERGE (c)-[:REFERENCES_ACT]->(a)
                    """,
                    case_id=cs.case_id,
                    act_id=cs.section.act_id,
                )

    return stats

