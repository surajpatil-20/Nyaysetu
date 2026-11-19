"""
Graph query service for NYAYASETU Judicial Knowledge Graph.
Supports querying Neo4j or PostgreSQL-derived graph model.
"""
import logging
from apps.cases.models import Case, CaseJudge, CaseParty, CaseCitation
from apps.courts.models import Court, Judge
from apps.legal.models import CaseSection
from apps.documents.models import Document
from .connection import get_neo4j_driver, check_neo4j_connection

logger = logging.getLogger(__name__)


def get_case_graph(case_id: int) -> dict:
    """
    Returns graph nodes and relationships for a case.
    Tries Neo4j first; falls back to PostgreSQL derived graph model if Neo4j is not connected.
    """
    try:
        case = Case.objects.select_related("court").get(pk=case_id)
    except Case.DoesNotExist:
        return None

    connected, _ = check_neo4j_connection()
    if connected:
        try:
            return _get_graph_from_neo4j(case)
        except Exception as e:
            logger.warning(f"Error querying Neo4j: {e}. Falling back to PostgreSQL-derived graph.")

    return _get_graph_from_postgres(case)


def _get_graph_from_neo4j(case: Case) -> dict:
    """Query Neo4j for the case subgraph."""
    driver = get_neo4j_driver()
    nodes_dict = {}
    links = []
    textual = []

    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Case {postgres_id: $case_id})
            OPTIONAL MATCH (c)-[r_court:FILED_IN]->(co:Court)
            OPTIONAL MATCH (c)-[r_judge:HEARD_BY]->(j:Judge)
            OPTIONAL MATCH (c)-[r_party:HAS_PARTY]->(p:Party)
            OPTIONAL MATCH (c)-[r_doc:HAS_DOCUMENT]->(d:Document)
            OPTIONAL MATCH (c)-[r_cite:CITES]->(c2:Case)
            OPTIONAL MATCH (c)-[r_sec:REFERENCES_SECTION]->(s:Section)
            OPTIONAL MATCH (c)-[r_act:REFERENCES_ACT]->(a:Act)
            RETURN c, r_court, co, r_judge, j, r_party, p, r_doc, d, r_cite, c2, r_sec, s, r_act, a
            """,
            case_id=case.id,
        )

        for record in result:
            c = record.get("c")
            if c:
                case_node_id = f"case_{c.get('postgres_id')}"
                if case_node_id not in nodes_dict:
                    nodes_dict[case_node_id] = {
                        "id": case_node_id,
                        "type": "Case",
                        "label": c.get("case_number", "Case"),
                        "data": dict(c),
                    }

            co = record.get("co")
            if co:
                co_id = f"court_{co.get('postgres_id')}"
                if co_id not in nodes_dict:
                    nodes_dict[co_id] = {
                        "id": co_id,
                        "type": "Court",
                        "label": co.get("name", "Court"),
                        "data": dict(co),
                    }
                links.append({
                    "source": case_node_id,
                    "target": co_id,
                    "type": "FILED_IN",
                    "label": "Filed In",
                })
                textual.append(f"Filed in {co.get('name')}")

            j = record.get("j")
            if j:
                j_id = f"judge_{j.get('postgres_id')}"
                if j_id not in nodes_dict:
                    nodes_dict[j_id] = {
                        "id": j_id,
                        "type": "Judge",
                        "label": j.get("name", "Judge"),
                        "data": dict(j),
                    }
                r_judge = record.get("r_judge")
                role = r_judge.get("role", "MEMBER") if r_judge else "MEMBER"
                links.append({
                    "source": case_node_id,
                    "target": j_id,
                    "type": "HEARD_BY",
                    "label": f"Heard By ({role})",
                    "role": role,
                })
                textual.append(f"Heard by Judge {j.get('name')} ({role})")

            p = record.get("p")
            if p:
                p_id = f"party_{p.get('postgres_id')}"
                if p_id not in nodes_dict:
                    nodes_dict[p_id] = {
                        "id": p_id,
                        "type": "Party",
                        "label": p.get("name", "Party"),
                        "data": dict(p),
                    }
                r_party = record.get("r_party")
                role = r_party.get("role", "PARTY") if r_party else "PARTY"
                links.append({
                    "source": case_node_id,
                    "target": p_id,
                    "type": "HAS_PARTY",
                    "label": f"Party ({role})",
                    "role": role,
                })
                textual.append(f"Party: {p.get('name')} ({role})")

            d = record.get("d")
            if d:
                d_id = f"doc_{d.get('postgres_id')}"
                if d_id not in nodes_dict:
                    nodes_dict[d_id] = {
                        "id": d_id,
                        "type": "Document",
                        "label": d.get("title", "Document"),
                        "data": dict(d),
                    }
                links.append({
                    "source": case_node_id,
                    "target": d_id,
                    "type": "HAS_DOCUMENT",
                    "label": "Document",
                })
                textual.append(f"Document: {d.get('title')}")

            c2 = record.get("c2")
            if c2:
                c2_id = f"case_{c2.get('postgres_id')}"
                if c2_id not in nodes_dict:
                    nodes_dict[c2_id] = {
                        "id": c2_id,
                        "type": "Case",
                        "label": c2.get("case_number", "Case"),
                        "data": dict(c2),
                    }
                r_cite = record.get("r_cite")
                cite_text = r_cite.get("citation_text", "") if r_cite else ""
                links.append({
                    "source": case_node_id,
                    "target": c2_id,
                    "type": "CITES",
                    "label": f"Cites {cite_text}",
                    "citation_text": cite_text,
                })
                textual.append(f"Cites precedent case: {c2.get('case_number')} ({cite_text})")

    # If Neo4j returned empty nodes (e.g. case not synced yet), fallback to postgres
    if not nodes_dict:
        return _get_graph_from_postgres(case)

    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "nodes": list(nodes_dict.values()),
        "links": links,
        "textual_relationships": textual,
        "source": "neo4j",
    }


def _get_graph_from_postgres(case: Case) -> dict:
    """Derive graph nodes and relationships directly from PostgreSQL."""
    nodes = []
    links = []
    textual = []

    case_node_id = f"case_{case.id}"
    nodes.append({
        "id": case_node_id,
        "type": "Case",
        "label": case.case_number or case.case_title,
        "data": {
            "postgres_id": case.id,
            "case_number": case.case_number,
            "title": case.case_title,
            "status": case.status,
            "decision_date": str(case.decision_date) if case.decision_date else None,
            "cnr_number": case.cnr_number,
        }
    })

    # Court
    if case.court:
        court_id = f"court_{case.court.id}"
        nodes.append({
            "id": court_id,
            "type": "Court",
            "label": case.court.court_name,
            "data": {
                "postgres_id": case.court.id,
                "name": case.court.court_name,
                "court_type": case.court.court_type,
            }
        })
        links.append({
            "source": case_node_id,
            "target": court_id,
            "type": "FILED_IN",
            "label": "Filed In",
        })
        textual.append(f"Filed in {case.court.court_name} ({case.court.get_court_type_display()})")

    # Judges
    for cj in CaseJudge.objects.filter(case=case).select_related("judge"):
        j = cj.judge
        j_id = f"judge_{j.id}"
        nodes.append({
            "id": j_id,
            "type": "Judge",
            "label": j.name,
            "data": {
                "postgres_id": j.id,
                "name": j.name,
                "designation": j.designation,
                "role": cj.role,
            }
        })
        links.append({
            "source": case_node_id,
            "target": j_id,
            "type": "HEARD_BY",
            "label": f"Heard By ({cj.get_role_display()})",
            "role": cj.role,
        })
        textual.append(f"Heard by {j.name} ({cj.get_role_display()})")

    # Parties
    for cp in CaseParty.objects.filter(case=case).select_related("party"):
        p = cp.party
        p_id = f"party_{p.id}"
        nodes.append({
            "id": p_id,
            "type": "Party",
            "label": p.name,
            "data": {
                "postgres_id": p.id,
                "name": p.name,
                "party_type": p.party_type,
                "role": cp.role,
            }
        })
        links.append({
            "source": case_node_id,
            "target": p_id,
            "type": "HAS_PARTY",
            "label": f"Party ({cp.get_role_display()})",
            "role": cp.role,
        })
        textual.append(f"Party: {p.name} as {cp.get_role_display()}")

    # Documents
    for doc in Document.objects.filter(case=case):
        d_id = f"doc_{doc.id}"
        nodes.append({
            "id": d_id,
            "type": "Document",
            "label": doc.title,
            "data": {
                "postgres_id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "page_count": doc.page_count,
            }
        })
        links.append({
            "source": case_node_id,
            "target": d_id,
            "type": "HAS_DOCUMENT",
            "label": "Document",
        })
        textual.append(f"Official Record: {doc.title} ({doc.get_document_type_display()})")

    # Citations made
    for cite in CaseCitation.objects.filter(source_case=case).exclude(cited_case__source_name="DEMO SOURCE").select_related("cited_case"):
        if cite.cited_case:
            c2 = cite.cited_case
            c2_id = f"case_{c2.id}"
            nodes.append({
                "id": c2_id,
                "type": "Case",
                "label": c2.case_number or c2.case_title,
                "data": {
                    "postgres_id": c2.id,
                    "case_number": c2.case_number,
                    "title": c2.case_title,
                }
            })
            links.append({
                "source": case_node_id,
                "target": c2_id,
                "type": "CITES",
                "label": f"Cites {cite.citation_text}",
                "citation_text": cite.citation_text,
            })
            textual.append(f"Cites precedent case: {c2.case_number} ({cite.citation_text})")
        else:
            textual.append(f"Cites external legal precedent: {cite.citation_text}")

    # Case Sections / Acts
    for cs in CaseSection.objects.filter(case=case).select_related("section", "section__act"):
        sec = cs.section
        s_id = f"sec_{sec.id}"
        nodes.append({
            "id": s_id,
            "type": "Section",
            "label": f"Sec. {sec.section_number}",
            "data": {
                "postgres_id": sec.id,
                "section_number": sec.section_number,
                "title": sec.title,
            }
        })
        links.append({
            "source": case_node_id,
            "target": s_id,
            "type": "REFERENCES_SECTION",
            "label": f"Sec {sec.section_number}",
        })
        textual.append(f"Invokes statutory provision: Section {sec.section_number}")

        if sec.act:
            act = sec.act
            a_id = f"act_{act.id}"
            nodes.append({
                "id": a_id,
                "type": "Act",
                "label": act.short_code or act.act_name,
                "data": {
                    "postgres_id": act.id,
                    "name": act.act_name,
                    "short_code": act.short_code,
                    "year": act.act_year,
                }
            })
            links.append({
                "source": s_id,
                "target": a_id,
                "type": "PART_OF",
                "label": "Part Of",
            })
            links.append({
                "source": case_node_id,
                "target": a_id,
                "type": "REFERENCES_ACT",
                "label": "References Act",
            })
            textual.append(f"Governed by Act: {act.act_name}")

    # Deduplicate nodes by id
    seen = set()
    unique_nodes = []
    for n in nodes:
        if n["id"] not in seen:
            seen.add(n["id"])
            unique_nodes.append(n)

    return {
        "case_id": case.id,
        "case_number": case.case_number,
        "nodes": unique_nodes,
        "links": links,
        "textual_relationships": textual,
        "source": "postgresql_derived",
    }

