#!/usr/bin/env python3
"""
arxiv 論文取得スクリプト
使い方:
    python fetch_arxiv.py --query "machine learning" --max 10
    python fetch_arxiv.py --query "data science" --max 5 --download --pdf-dir topics/example/papers
"""

import arxiv
import argparse
import json
import requests
from pathlib import Path


def fetch_papers(query: str, max_results: int = 10, sort_by: str = "relevance") -> list[dict]:
    sort_map = {
        "relevance": arxiv.SortCriterion.Relevance,
        "recent":    arxiv.SortCriterion.SubmittedDate,
        "updated":   arxiv.SortCriterion.LastUpdatedDate,
    }

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_map.get(sort_by, arxiv.SortCriterion.Relevance),
    )

    papers = []
    for result in client.results(search):
        papers.append({
            "arxiv_id":   result.entry_id.split("/")[-1],
            "title":      result.title,
            "authors":    [a.name for a in result.authors],
            "abstract":   result.summary,
            "published":  result.published.strftime("%Y-%m-%d"),
            "updated":    result.updated.strftime("%Y-%m-%d"),
            "categories": result.categories,
            "url":        result.entry_id,
            "pdf_url":    result.pdf_url,
        })

    return papers


def download_pdf(pdf_url: str, dest_path: Path) -> bool:
    if dest_path.exists():
        print(f"    スキップ（既存）: {dest_path.name}")
        return True
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        dest_path.write_bytes(response.content)
        print(f"    ダウンロード完了: {dest_path.name}")
        return True
    except Exception as e:
        print(f"    ダウンロード失敗: {e}")
        return False


def convert_to_markdown(pdf_path: Path, md_path: Path) -> bool:
    if md_path.exists():
        print(f"    スキップ（既存）: {md_path.name}")
        return True
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(str(pdf_path))
        md_path.write_text(result.text_content, encoding="utf-8")
        print(f"    Markdown変換完了: {md_path.name}")
        return True
    except Exception as e:
        print(f"    Markdown変換失敗: {e}")
        return False


def print_papers(papers: list[dict]) -> None:
    for i, p in enumerate(papers, 1):
        print(f"\n{'='*60}")
        print(f"[{i}] {p['title']}")
        print(f"    arxiv ID : {p['arxiv_id']}")
        print(f"    著者     : {', '.join(p['authors'][:3])}{'...' if len(p['authors']) > 3 else ''}")
        print(f"    公開日   : {p['published']}")
        print(f"    カテゴリ : {', '.join(p['categories'])}")
        print(f"    URL      : {p['url']}")
        print(f"    概要     : {p['abstract'][:200].replace(chr(10), ' ')}...")


def main():
    parser = argparse.ArgumentParser(description="arxiv論文取得スクリプト")
    parser.add_argument("--query",    "-q", required=True, help="検索クエリ（例: 'machine learning'）")
    parser.add_argument("--max",      "-m", type=int, default=10, help="取得件数（デフォルト: 10）")
    parser.add_argument("--sort",     "-s", choices=["relevance", "recent", "updated"],
                        default="relevance", help="ソート順（デフォルト: relevance）")
    parser.add_argument("--output",   "-o", help="JSONファイルに保存する場合はパスを指定")
    parser.add_argument("--download", "-d", action="store_true", help="PDFをダウンロードしてMarkdownに変換する")
    parser.add_argument("--pdf-dir",  help="PDF・Markdownの保存先ディレクトリ")
    args = parser.parse_args()

    if args.download and not args.pdf_dir:
        parser.error("--download を使う場合は --pdf-dir を指定してください")

    print(f"検索中: '{args.query}' (最大{args.max}件, ソート: {args.sort})")
    papers = fetch_papers(args.query, args.max, args.sort)
    print(f"{len(papers)}件取得しました")

    print_papers(papers)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"\nJSONに保存しました: {args.output}")

    if args.download:
        pdf_dir = Path(args.pdf_dir)
        pdf_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nPDF・Markdownを {pdf_dir}/ に保存します")

        for p in papers:
            arxiv_id = p["arxiv_id"].replace("/", "_")
            print(f"\n  [{arxiv_id}] {p['title'][:50]}...")
            pdf_path = pdf_dir / f"{arxiv_id}.pdf"
            md_path  = pdf_dir / f"{arxiv_id}.md"

            if download_pdf(p["pdf_url"], pdf_path):
                convert_to_markdown(pdf_path, md_path)


if __name__ == "__main__":
    main()
