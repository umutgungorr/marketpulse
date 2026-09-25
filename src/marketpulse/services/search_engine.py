"""Strict asset search engine with zero junk results and category isolation."""

from dataclasses import dataclass
from typing import Any
from marketpulse.models import Asset
from marketpulse.services.asset_registry import AssetRegistry


@dataclass
class SearchResult:
    query: str
    asset_type_filter: str
    total_matches: int
    results: list[dict[str, Any]]
    suggestions: list[str]
    message_tr: str
    message_en: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "asset_type_filter": self.asset_type_filter,
            "total_matches": self.total_matches,
            "results": self.results,
            "suggestions": self.suggestions,
            "message_tr": self.message_tr,
            "message_en": self.message_en,
        }


def normalize_text(text: str) -> str:
    """Normalizes Turkish/English characters, accents, and case for robust search."""
    mapping = {
        "I": "i", "ı": "i",
        "İ": "i", "i": "i",
        "Ğ": "g", "ğ": "g",
        "Ü": "u", "ü": "u",
        "Ş": "s", "ş": "s",
        "Ö": "o", "ö": "o",
        "Ç": "c", "ç": "c",
    }
    return "".join(mapping.get(ch, ch.lower()) for ch in text)


class SearchEngine:
    def __init__(self, registry: AssetRegistry | None = None):
        self.registry = registry or AssetRegistry()

    def search(self, query: str, asset_type: str = "all", limit: int = 10) -> SearchResult:
        """
        Executes strict, high-confidence search.
        Rejects random gibberish and never returns irrelevant items.
        """
        q = (query or "").strip()
        q_norm = normalize_text(q)
        q_compact = q_norm.replace(" ", "")
        type_filter = (asset_type or "all").lower()

        # Popular baseline suggestions for empty or non-matching states
        popular_suggestions = ["THYAO", "BTC", "ASELS", "ETH", "NVDA", "GARAN"]

        if not q_norm:
            # Empty query: return empty or category list
            return SearchResult(
                query="",
                asset_type_filter=type_filter,
                total_matches=0,
                results=[],
                suggestions=popular_suggestions,
                message_tr="Aramak için hisse veya kripto sembolü yazın.",
                message_en="Type a stock or crypto symbol to search.",
            )

        # Base pool filtered by category
        pool = self.registry.list_all(None if type_filter == "all" else type_filter)

        exact_symbol_matches: list[Asset] = []
        prefix_symbol_matches: list[Asset] = []
        name_matches: list[Asset] = []
        description_matches: list[Asset] = []

        for asset in pool:
            sym_norm = normalize_text(asset.symbol)
            name_norm = normalize_text(asset.name)
            name_compact = name_norm.replace(" ", "")
            desc_tr_norm = normalize_text(asset.description_tr)
            desc_en_norm = normalize_text(asset.description_en)

            if sym_norm == q_norm:
                exact_symbol_matches.append(asset)
            elif sym_norm.startswith(q_norm):
                prefix_symbol_matches.append(asset)
            elif q_norm in name_norm or (len(q_compact) >= 4 and q_compact in name_compact):
                name_matches.append(asset)
            elif len(q_norm) >= 3 and (q_norm in desc_tr_norm or q_norm in desc_en_norm):
                description_matches.append(asset)

        # Combine with strict priority ranking
        ranked_assets = (
            exact_symbol_matches
            + prefix_symbol_matches
            + name_matches
            + description_matches
        )

        # Deduplicate while preserving rank order
        seen = set()
        deduped: list[Asset] = []
        for item in ranked_assets:
            if item.symbol not in seen:
                seen.add(item.symbol)
                deduped.append(item)

        results = deduped[:limit]

        if not results:
            # Strict rejection: Do not fuzzily show unrelated symbols!
            # Instead, offer helpful known suggestions
            suggestions = [s for s in popular_suggestions if s.lower() != q][:4]
            return SearchResult(
                query=query,
                asset_type_filter=type_filter,
                total_matches=0,
                results=[],
                suggestions=suggestions,
                message_tr=f"'{query}' ile eşleşen doğrulanmış hisse veya coin bulunamadı.",
                message_en=f"No verified stock or coin found matching '{query}'.",
            )

        return SearchResult(
            query=query,
            asset_type_filter=type_filter,
            total_matches=len(results),
            results=[a.to_dict() for a in results],
            suggestions=[],
            message_tr=f"{len(results)} sonuç bulundu.",
            message_en=f"{len(results)} match(es) found.",
        )
