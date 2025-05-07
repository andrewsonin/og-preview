#!/usr/bin/env bash
import argparse

from og_preview import generate_og_images, ArticleInfo

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates OG Image")
    parser.add_argument('--title', required=True, type=str, help="Title text")
    parser.add_argument('--description', required=True, type=str, help="Description text")
    parser.add_argument('--author', required=True, type=str, help="Author name")
    parser.add_argument('--url', required=True, type=str, help="Article URL")
    parser.add_argument('--avatar', required=True, type=str, help="Path to author avatar image")
    parser.add_argument('--logo', required=True, type=str, help="Path to logo image")
    parser.add_argument('--output', required=True, type=str, help="Path to output file")

    args = parser.parse_args()

    generate_og_images(
        ArticleInfo(
            title=args.title,
            description=args.description,
            author=args.author,
            url=args.url,
            output_path=args.output
        ),
        avatar_path=args.avatar,
        logo_path=args.logo,
    )
