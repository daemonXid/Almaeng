"""
🔮 Management Command: Generate Embeddings

모든 Supplement와 MFDSHealthFood에 대해 임베딩 벡터를 생성합니다.

Usage:
    python manage.py generate_embeddings
    python manage.py generate_embeddings --supplements-only
    python manage.py generate_embeddings --mfds-only
"""

from django.core.management.base import BaseCommand

from domains.features.supplements.interface import (
    generate_embedding_for_mfds,
    generate_embedding_for_supplement,
    get_all_supplements,
    get_mfds_count,
    search_mfds_products,
)


class Command(BaseCommand):
    help = "Generate embedding vectors for all supplements and MFDS products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--supplements-only",
            action="store_true",
            help="Generate embeddings only for Supplements",
        )
        parser.add_argument(
            "--mfds-only",
            action="store_true",
            help="Generate embeddings only for MFDSHealthFood",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of items to process",
        )

    def handle(self, *args, **options):
        supplements_only = options["supplements_only"]
        mfds_only = options["mfds_only"]
        limit = options["limit"]

        if not supplements_only:
            self.stdout.write("🔄 Generating embeddings for MFDSHealthFood...")
            mfds_products = search_mfds_products("", limit=limit or get_mfds_count())
            total_mfds = mfds_products.count()
            processed_mfds = 0
            
            for mfds in mfds_products:
                if mfds.embedding is None:
                    embedding = generate_embedding_for_mfds(mfds)
                    if embedding:
                        processed_mfds += 1
                        self.stdout.write(
                            f"  ✅ {mfds.product_name[:50]}... ({processed_mfds}/{total_mfds})"
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠️ Failed: {mfds.product_name[:50]}...")
                        )
                else:
                    self.stdout.write(f"  ⏭️ Skipped (already has embedding): {mfds.product_name[:50]}...")
            
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ Processed {processed_mfds} MFDS products")
            )

        if not mfds_only:
            self.stdout.write("\n🔄 Generating embeddings for Supplements...")
            supplements = get_all_supplements()
            if limit:
                supplements = supplements[:limit]
            
            total_supplements = supplements.count()
            processed_supplements = 0
            
            for supplement in supplements:
                if supplement.embedding is None:
                    embedding = generate_embedding_for_supplement(supplement)
                    if embedding:
                        processed_supplements += 1
                        self.stdout.write(
                            f"  ✅ {supplement.name[:50]}... ({processed_supplements}/{total_supplements})"
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠️ Failed: {supplement.name[:50]}...")
                        )
                else:
                    self.stdout.write(f"  ⏭️ Skipped (already has embedding): {supplement.name[:50]}...")
            
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ Processed {processed_supplements} Supplements")
            )

        self.stdout.write(self.style.SUCCESS("\n🎉 Embedding generation complete!"))
