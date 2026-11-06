"""
Management command to sync judicial records from PostgreSQL to Neo4j.
"""
from django.core.management.base import BaseCommand
from apps.graph.sync import sync_knowledge_graph


class Command(BaseCommand):
    help = "Synchronizes cases and entities from PostgreSQL to Neo4j Knowledge Graph."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Count records and preview graph operations without writing to Neo4j.',
        )
        parser.add_argument(
            '--case-id',
            type=int,
            default=None,
            help='Sync a specific case by its PostgreSQL ID.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        case_id = options.get('case_id', None)

        self.stdout.write("Starting Judicial Knowledge Graph synchronization...")
        if dry_run:
            self.stdout.write(self.style.WARNING("Running in DRY-RUN mode."))

        stats = sync_knowledge_graph(dry_run=dry_run, case_id=case_id)

        self.stdout.write(f"Neo4j Connected: {stats['neo4j_connected']} ({stats.get('connection_message')})")
        self.stdout.write(f"Cases Synced: {stats['cases_synced']}")
        self.stdout.write(f"Courts Synced: {stats['courts_synced']}")
        self.stdout.write(f"Judges Synced: {stats['judges_synced']}")
        self.stdout.write(f"Parties Synced: {stats['parties_synced']}")
        self.stdout.write(f"Documents Synced: {stats['documents_synced']}")
        self.stdout.write(f"Acts Synced: {stats['acts_synced']}")
        self.stdout.write(f"Sections Synced: {stats['sections_synced']}")
        self.stdout.write(f"Total Relationships: {stats['relationships_created']}")

        self.stdout.write(self.style.SUCCESS("Knowledge Graph synchronization process finished successfully."))

