#!/usr/bin/env python3
"""
PubMed Abstract to RIS Converter

This script converts PubMed abstract text files to RIS (Research Information Systems) format.
RIS files can be imported into reference management software like EndNote, Mendeley, or Zotero.

Usage:
    python pubmed_to_ris.py input_file.txt output_file.ris
    python pubmed_to_ris.py input_file.txt  # Creates input_file.ris
"""

import re
import sys
import os
from typing import Dict, List, Optional


class PubMedToRISConverter:
    def __init__(self):
        # Comprehensive mapping of PubMed fields to RIS tags
        # Based on the full RIS specification
        self.field_mappings = {
            # Core fields
            'PMID': 'AN',  # Accession Number
            'Title': 'TI',  # Title (primary)
            'Secondary Title': 'T2',  # Secondary Title
            'Tertiary Title': 'T3',  # Tertiary Title
            'Authors': 'AU',  # Author
            'Author': 'AU',  # Author (alternative)
            'Primary Authors': 'A1',  # Primary Authors
            'Secondary Authors': 'A2',  # Secondary Authors (Editors)
            'Editors': 'A2',  # Editors
            'Editor': 'A2',  # Editor
            'Tertiary Authors': 'A3',  # Tertiary Authors
            'Subsidiary Authors': 'A4',  # Subsidiary Authors
            'Abstract': 'AB',  # Abstract
            'Notes': 'N1',  # Notes
            'Additional Notes': 'N2',  # Additional Notes
            
            # Publication details
            'Journal': 'JO',  # Journal Name (full)
            'Journal Abbreviation': 'J2',  # Journal Abbreviation
            'Secondary Title': 'T2',  # Often journal name
            'Year': 'PY',  # Publication Year (primary)
            'Publication Year': 'Y1',  # Publication Year (alternative)
            'Secondary Year': 'Y2',  # Secondary Year
            'Volume': 'VL',  # Volume
            'Issue': 'IS',  # Issue Number
            'Number': 'IS',  # Issue Number (alternative)
            'Pages': 'SP',  # Start Page
            'Start Page': 'SP',  # Start Page
            'End Page': 'EP',  # End Page
            'Number of Pages': 'NV',  # Number of Volumes/Pages
            'Edition': 'ET',  # Edition
            
            # Identifiers
            'DOI': 'DO',  # DOI
            'ISBN': 'SN',  # ISBN/ISSN
            'ISSN': 'SN',  # ISSN
            'Call Number': 'CN',  # Call Number
            'Database': 'DB',  # Name of Database
            'Database Provider': 'DP',  # Database Provider
            'Accession Number': 'AN',  # Accession Number
            'Reference ID': 'ID',  # Reference ID
            
            # Publication info
            'Publisher': 'PB',  # Publisher
            'Place Published': 'CY',  # Place Published/Country
            'Country': 'CY',  # Country
            'City': 'CY',  # City
            'Publication Type': 'PT',  # Publication Type
            'Type of Work': 'M3',  # Type of Work
            'Language': 'LA',  # Language
            'Original Publication': 'OP',  # Original Publication
            'Reprint Edition': 'RP',  # Reprint Edition
            'Reviewed Item': 'RI',  # Reviewed Item
            
            # Keywords and subjects
            'Keywords': 'KW',  # Keywords
            'Keyword': 'KW',  # Keyword
            'Research Notes': 'RN',  # Research Notes
            
            # Author information
            'Affiliation': 'AD',  # Author Address
            'Author Address': 'AD',  # Author Address
            'Corporate Author': 'AU',  # Corporate Author
            
            # Dates
            'Date': 'DA',  # Date
            'Access Date': 'Y2',  # Access Date
            'Copyright Date': 'Y2',  # Copyright Date
            
            # URLs and files
            'URL': 'UR',  # URL
            'File Attachments': 'L1',  # File Attachments
            'Link to PDF': 'L1',  # Link to PDF
            'Related Records': 'L2',  # Related Records
            'Image': 'L4',  # Image
            
            # Custom fields
            'Custom 1': 'C1',  # Custom 1
            'Custom 2': 'C2',  # Custom 2
            'Custom 3': 'C3',  # Custom 3
            'Custom 4': 'C4',  # Custom 4
            'Custom 5': 'C5',  # Custom 5
            'Custom 6': 'C6',  # Custom 6
            'Custom 7': 'C7',  # Custom 7
            'Custom 8': 'C8',  # Custom 8
            
            # Specialized fields
            'Caption': 'CA',  # Caption
            'Short Title': 'ST',  # Short Title
            'Translated Author': 'TA',  # Translated Author
            'Translated Title': 'TT',  # Translated Title
            'User Definable 1': 'U1',  # User Definable 1
            'User Definable 2': 'U2',  # User Definable 2
            'User Definable 3': 'U3',  # User Definable 3
            'User Definable 4': 'U4',  # User Definable 4
            'User Definable 5': 'U5',  # User Definable 5
            'Availability': 'AV',  # Availability
            'Location in Archives': 'AV',  # Location in Archives
            'Legal Note': 'LB',  # Legal Note
            'Government Document Number': 'GP',  # Government Document Number
            'Patent Assignee': 'PA',  # Patent Assignee
            'Patent Country': 'PC',  # Patent Country
            'Patent Number': 'PN',  # Patent Number
            'Conference Name': 'BT',  # Conference Name (Book Title field)
            'Conference Location': 'CY',  # Conference Location
            'Conference Date': 'Y2',  # Conference Date
            'Series Title': 'T3',  # Series Title
            'Series Editor': 'A3',  # Series Editor
            'PMCID': 'AN',  # PubMed Central ID (mapped to Accession Number)
            'MeSH Terms': 'KW',  # MeSH Terms (mapped to Keywords)
            'Chemical List': 'KW',  # Chemical List (mapped to Keywords)
            'Grant Number': 'FU',  # Funding/Grant Number
            'Funding': 'FU',  # Funding
        }
        
        # Publication type mappings (PubMed to RIS)
        self.publication_types = {
            'Journal Article': 'JOUR',
            'Review': 'JOUR',
            'Systematic Review': 'JOUR', 
            'Meta-Analysis': 'JOUR',
            'Case Reports': 'JOUR',
            'Editorial': 'JOUR',
            'Letter': 'JOUR',
            'Comment': 'JOUR',
            'News': 'JOUR',
            'Book': 'BOOK',
            'Book Chapter': 'CHAP',
            'Conference Paper': 'CONF',
            'Conference Abstract': 'ABST',
            'Thesis': 'THES',
            'Dissertation': 'THES',
            'Report': 'RPRT',
            'Technical Report': 'RPRT',
            'Patent': 'PAT',
            'Webpage': 'ELEC',
            'Electronic Article': 'EJOUR',
            'Magazine Article': 'MGZN',
            'Newspaper Article': 'NEWS',
            'Government Document': 'GOVDOC',
            'Legal Rule or Regulation': 'LEGAL',
            'Manuscript': 'MANSCPT',
            'Map': 'MAP',
            'Personal Communication': 'PCOMM',
            'Unpublished Work': 'UNPB',
            'Generic': 'GEN',
        }
        
        # Common RIS publication types for fallback
        self.default_pub_type = 'JOUR'  # Default to Journal Article
    
    def parse_pubmed_text(self, text: str) -> List[Dict[str, str]]:
        """
        Parse PubMed text format and extract article information.
        
        The format is:
        1. Numbered entry with journal citation
        2. Title (on its own line)
        3. Authors (on their own line)
        4. "Author information:" section
        5. Abstract (starts after author info)
        6. DOI, PMCID, PMID at the end
        
        Args:
            text: Raw text content from PubMed file
            
        Returns:
            List of dictionaries containing article data
        """
        articles = []
        
        # Split articles by numbered entries (e.g., "1. ", "2. ", etc.)
        # Pattern: number followed by period and space, then journal citation
        article_blocks = re.split(r'\n(?=\d+\.\s+[A-Z])', text.strip())
        
        for block in article_blocks:
            if not block.strip():
                continue
                
            article = self._parse_single_article(block)
            if article:
                articles.append(article)
        
        return articles
    
    def _parse_single_article(self, text: str) -> Optional[Dict[str, str]]:
        """Parse a single article block using spacing/blank lines as section boundaries."""
        article = {}
        # Keep original lines with spacing info - don't filter blank lines yet
        all_lines = text.split('\n')
        
        if not all_lines:
            return None
        
        # Find section boundaries using blank lines
        sections = []
        current_section = []
        
        for i, line in enumerate(all_lines):
            line_stripped = line.strip()
            
            # If we hit a blank line, save current section and start new one
            if not line_stripped:
                if current_section:
                    sections.append(current_section)
                    current_section = []
            else:
                current_section.append((i, line_stripped))
        
        # Don't forget the last section
        if current_section:
            sections.append(current_section)
        
        # Now parse sections based on their position and content
        # Section 0: Citation (first line(s))
        # Section 1: Title
        # Section 2: Authors
        # Section 3: Author information header + affiliations
        # Section 4+: Abstract and metadata
        
        if not sections:
            return None
        
        # Section 0: Parse citation (first section)
        if sections:
            citation_section = sections[0]
            citation_lines = [line for _, line in citation_section]
            citation_text = ' '.join(citation_lines)
        
        # Extract year (look for 4-digit year, prefer the one after journal name)
        year_match = re.search(r'\.\s+(\d{4})\s+[A-Z][a-z]{2}', citation_text)
        if not year_match:
            year_match = re.search(r'\s+(\d{4})\s+', citation_text)
        if year_match:
            article['Year'] = year_match.group(1)
        
        # Extract journal name (everything from number to first year or semicolon)
        journal_match = re.match(r'^\d+\.\s+(.+?)(?:\s+\d{4}|\s*;|\s+doi)', citation_text)
        if journal_match:
            journal_full = journal_match.group(1).strip()
            # Extract journal name (before the year/date)
            journal_name = journal_full.split('.')[0] if '.' in journal_full else journal_full
            # Clean up journal name
            journal_name = re.sub(r'\s+', ' ', journal_name).strip()
            if journal_name:
                article['Journal'] = journal_name
        
        # Extract volume, issue, pages from citation
        vol_match = re.search(r';(\d+)\((\d+)\):(\d+)-?(\d+)?', citation_text)
        if vol_match:
            article['Volume'] = vol_match.group(1)
            article['Issue'] = vol_match.group(2)
            start_page = vol_match.group(3)
            end_page = vol_match.group(4)
            if end_page:
                article['Pages'] = f"{start_page}-{end_page}"
            else:
                article['Pages'] = start_page
        else:
            # Try simpler volume pattern (without issue)
            vol_match = re.search(r';(\d+):(\d+)-?(\d+)?', citation_text)
            if vol_match:
                article['Volume'] = vol_match.group(1)
                start_page = vol_match.group(2)
                end_page = vol_match.group(3)
                if end_page:
                    article['Pages'] = f"{start_page}-{end_page}"
                else:
                    article['Pages'] = start_page
        
        # Extract DOI from citation (might be on first or second line)
        # DOI format: doi: 10.xxxx/xxxx or doi: 10.xxxx/xxxx.
        doi_match = re.search(r'doi[:\s]+(10\.[^\s]+)', citation_text, re.IGNORECASE)
        if doi_match:
            doi_value = doi_match.group(1).strip()
            # Remove trailing period if present
            doi_value = doi_value.rstrip('.')
            article['DOI'] = doi_value
        
        # Section 1: Title (second section, after blank line following citation)
        if len(sections) > 1:
            title_section = sections[1]
            title_lines = [line for _, line in title_section]
            title_text = ' '.join(title_lines).strip()
            if title_text:
                article['Title'] = title_text
        
        # Section 2: Authors (third section, after blank line following title)
        if len(sections) > 2:
            author_section = sections[2]
            author_lines = [line for _, line in author_section]
            author_text = ' '.join(author_lines).strip()
            if author_text:
                article['Authors'] = author_text
        
        # Section 3: Author information (fourth section) - skip this, it's just affiliations
        # Section 4+: Abstract starts here (after blank line following author info)
        # Collect abstract from section 4 onwards until we hit metadata markers
        abstract_lines = []
        
        if len(sections) > 3:
            # Start from section 4 (index 3 is author info, index 4+ is abstract/metadata)
            for section_idx in range(4, len(sections)):
                section = sections[section_idx]
                section_lines = [line for _, line in section]
                section_text = ' '.join(section_lines).strip()
                
                # Skip sections that are citation references (e.g., "Comment in", "Erratum in", etc.)
                if re.match(r'^(Comment in|Erratum in|Retraction in|Retraction of|Update in|Update of|Summary for patients in)', section_text, re.IGNORECASE):
                    continue
                
                # Stop at common metadata markers
                if re.match(r'^(DOI|PMID|PMCID|Copyright|Conflict)', section_text, re.IGNORECASE):
                    break
                
                # This section is part of the abstract
                abstract_lines.extend(section_lines)
        
        if abstract_lines:
            abstract_text = ' '.join(abstract_lines)
            # Clean up: remove citation references from the beginning of abstract
            # Pattern: "Comment in [Journal]. [Date];[Volume]([Issue]):[Pages]. doi: [DOI]."
            # This handles cases where "Comment in" and citation are in the same section
            abstract_text = re.sub(r'^(Comment in|Erratum in|Retraction in|Retraction of|Update in|Update of|Summary for patients in)\s+[^.]+\.[^;]*;\d+\(\d+\):[^.]*\.\s*(?:doi:\s+[^\s]+\s*\.\s*)?', '', abstract_text, flags=re.IGNORECASE)
            # Also handle simpler patterns without volume/issue
            abstract_text = re.sub(r'^(Comment in|Erratum in|Retraction in|Retraction of|Update in|Update of|Summary for patients in)\s+[^.]+\.[^.]*\.\s*(?:doi:\s+[^\s]+\s*\.\s*)?', '', abstract_text, flags=re.IGNORECASE)
            # Remove any trailing copyright notices that might have been included
            abstract_text = re.sub(r'\s*Copyright[^.]*\.\s*$', '', abstract_text, flags=re.IGNORECASE)
            abstract_text = abstract_text.strip()
            if abstract_text and len(abstract_text) > 10:  # Only add if substantial
                article['Abstract'] = abstract_text
        
        # Extract DOI, PMCID, PMID from all sections (check all sections for metadata)
        for section in sections:
            for _, line in section:
                # Extract DOI (format: DOI: 10.xxxx/xxxx)
                doi_match = re.search(r'DOI[:\s]+(10\.[^\s]+)', line, re.IGNORECASE)
                if doi_match and 'DOI' not in article:
                    doi_value = doi_match.group(1).strip().rstrip('.')
                    article['DOI'] = doi_value
                
                # Extract PMID
                pmid_match = re.search(r'PMID[:\s]+(\d+)', line, re.IGNORECASE)
                if pmid_match:
                    article['PMID'] = pmid_match.group(1)
                
                # Extract PMCID
                pmcid_match = re.search(r'PMCID[:\s]+(PMC\d+)', line, re.IGNORECASE)
                if pmcid_match:
                    article['PMCID'] = pmcid_match.group(1)
        
        return article if article else None
    
    def _identify_field(self, line: str) -> Optional[Dict[str, str]]:
        """Identify field type and extract content (legacy method, kept for compatibility)."""
        # This method is no longer used in the new parser but kept for compatibility
        patterns = [
            (r'^Title[:\s]+(.+)', 'Title'),
            (r'^Authors?[:\s]+(.+)', 'Authors'),
            (r'^Abstract[:\s]+(.+)', 'Abstract'),
            (r'^Journal[:\s]+(.+)', 'Journal'),
            (r'^Year[:\s]+(.+)', 'Year'),
            (r'^DOI[:\s]+(.+)', 'DOI'),
            (r'^PMID[:\s]+(.+)', 'PMID'),
        ]
        
        for pattern, field in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return {'field': field, 'content': match.group(1)}
        
        return None
    
    def convert_to_ris(self, articles: List[Dict[str, str]]) -> str:
        """
        Convert parsed articles to RIS format.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            RIS formatted string
        """
        ris_content = []
        
        for article in articles:
            # Determine publication type
            pub_type = self.default_pub_type
            if 'Publication Type' in article:
                pub_type_text = article['Publication Type']
                # Try to match with our publication type mappings
                for key, value in self.publication_types.items():
                    if key.lower() in pub_type_text.lower():
                        pub_type = value
                        break
            
            # Start with record type
            ris_content.append(f"TY  - {pub_type}")
            
            # Convert each field to RIS format
            for field, content in article.items():
                ris_tag = self.field_mappings.get(field)
                if ris_tag:
                    # Handle multiple authors
                    if field in ['Authors', 'Author', 'Primary Authors', 'Secondary Authors', 'Editors', 'Editor'] and ris_tag in ['AU', 'A1', 'A2']:
                        authors = self._parse_authors(content)
                        for author in authors:
                            ris_content.append(f"{ris_tag}  - {author}")
                    # Handle keywords and MeSH terms
                    elif field in ['Keywords', 'Keyword', 'MeSH Terms', 'Chemical List'] and ris_tag == 'KW':
                        keywords = self._parse_keywords(content)
                        for keyword in keywords:
                            ris_content.append(f"{ris_tag}  - {keyword}")
                    # Handle pages
                    elif field == 'Pages' and ris_tag == 'SP':
                        start_page, end_page = self._parse_pages(content)
                        if start_page:
                            ris_content.append(f"SP  - {start_page}")
                        if end_page:
                            ris_content.append(f"EP  - {end_page}")
                    # Handle publication type (already handled above)
                    elif field == 'Publication Type':
                        continue  # Already processed
                    else:
                        # Clean content and add
                        clean_content = self._clean_content(content)
                        if clean_content:
                            ris_content.append(f"{ris_tag}  - {clean_content}")
            
            # End record
            ris_content.append("ER  - ")
            ris_content.append("")  # Empty line between records
        
        return '\n'.join(ris_content)
    
    def _parse_authors(self, author_string: str) -> List[str]:
        """Parse author string into individual authors."""
        # Common delimiters for authors
        authors = re.split(r'[;,]|(?:\s+and\s+)', author_string)
        
        cleaned_authors = []
        for author in authors:
            author = author.strip()
            if author and author not in cleaned_authors:
                # Remove ALL affiliation numbers in parentheses (like (1), (2), (3), etc.)
                # This handles patterns like "Name(1)", "Name(1)(2)", "Name(1)."
                author = re.sub(r'\([^)]*\)', '', author)  # Remove all parentheses and contents
                # Remove trailing periods and clean up
                author = author.rstrip('.').strip()
                # Normalize spaces
                author = re.sub(r'\s+', ' ', author)
                if author:  # Only add if there's still content after cleaning
                    cleaned_authors.append(author)
        
        return cleaned_authors
    
    def _parse_keywords(self, keyword_string: str) -> List[str]:
        """Parse keyword string into individual keywords."""
        keywords = re.split(r'[;,]', keyword_string)
        return [kw.strip() for kw in keywords if kw.strip()]
    
    def _parse_pages(self, page_string: str) -> tuple:
        """Parse page range into start and end pages."""
        page_match = re.search(r'(\d+)(?:\s*[-–—]\s*(\d+))?', page_string)
        if page_match:
            start_page = page_match.group(1)
            end_page = page_match.group(2)
            return start_page, end_page
        return None, None
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove common prefixes/suffixes that might have been included
        content = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', content)
        
        return content
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert a PubMed text file to RIS format.
        
        Args:
            input_path: Path to input PubMed text file
            output_path: Path to output RIS file (optional)
            
        Returns:
            Path to created RIS file
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(input_path, 'r', encoding='latin-1') as f:
                text = f.read()
        
        # Parse articles
        articles = self.parse_pubmed_text(text)
        
        if not articles:
            print("Warning: No articles found in the input file.")
            return ""
        
        # Convert to RIS
        ris_content = self.convert_to_ris(articles)
        
        # Determine output path
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}.ris"
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ris_content)
        
        print(f"Converted {len(articles)} article(s) to RIS format.")
        print(f"Output saved to: {output_path}")
        
        return output_path
    
    def list_supported_tags(self) -> Dict[str, str]:
        """
        Return a dictionary of all supported RIS tags and their meanings.
        
        Returns:
            Dictionary mapping RIS tags to their descriptions
        """
        ris_tag_descriptions = {
            'TY': 'Type of reference (must be first)',
            'A1': 'Primary Authors',
            'A2': 'Secondary Authors (Editors)',
            'A3': 'Tertiary Authors',
            'A4': 'Subsidiary Authors', 
            'AB': 'Abstract',
            'AD': 'Author Address',
            'AN': 'Accession Number',
            'AU': 'Author',
            'AV': 'Location in Archives/Availability',
            'BT': 'Book Title',
            'C1': 'Custom 1',
            'C2': 'Custom 2', 
            'C3': 'Custom 3',
            'C4': 'Custom 4',
            'C5': 'Custom 5',
            'C6': 'Custom 6',
            'C7': 'Custom 7',
            'C8': 'Custom 8',
            'CA': 'Caption',
            'CN': 'Call Number',
            'CP': 'Misc',
            'CT': 'Title of unpublished reference',
            'CY': 'Place Published/Country',
            'DA': 'Date',
            'DB': 'Name of Database',
            'DO': 'DOI',
            'DP': 'Database Provider',
            'ED': 'Editor',
            'EP': 'End Page',
            'ER': 'End of Reference (must be last)',
            'ET': 'Edition',
            'FU': 'Funding/Grant Number',
            'GP': 'Government Document Number',
            'ID': 'Reference ID',
            'IS': 'Issue Number',
            'J2': 'Journal Abbreviation',
            'JO': 'Journal Name',
            'KW': 'Keywords',
            'L1': 'File Attachments',
            'L2': 'Related Records',
            'L4': 'Image',
            'LA': 'Language',
            'LB': 'Legal Note',
            'M3': 'Type of Work',
            'N1': 'Notes',
            'N2': 'Additional Notes',
            'NV': 'Number of Volumes',
            'OP': 'Original Publication',
            'PA': 'Patent Assignee',
            'PB': 'Publisher',
            'PC': 'Patent Country',
            'PN': 'Patent Number',
            'PT': 'Publication Type',
            'PY': 'Publication Year',
            'RI': 'Reviewed Item',
            'RN': 'Research Notes',
            'RP': 'Reprint Edition',
            'SN': 'ISBN/ISSN',
            'SP': 'Start Page',
            'ST': 'Short Title',
            'T2': 'Secondary Title',
            'T3': 'Tertiary Title',
            'TA': 'Translated Author',
            'TI': 'Title',
            'TT': 'Translated Title',
            'U1': 'User Definable 1',
            'U2': 'User Definable 2',
            'U3': 'User Definable 3',
            'U4': 'User Definable 4',
            'U5': 'User Definable 5',
            'UR': 'URL',
            'VL': 'Volume',
            'Y1': 'Publication Year (alternative)',
            'Y2': 'Secondary Year/Access Date',
        }
        return ris_tag_descriptions
    
    def print_supported_tags(self):
        """Print all supported RIS tags with descriptions."""
        tags = self.list_supported_tags()
        print("Supported RIS Tags:")
        print("=" * 50)
        for tag, description in sorted(tags.items()):
            print(f"{tag:3} - {description}")
    
    def list_publication_types(self) -> Dict[str, str]:
        """Return supported publication types."""
        return self.publication_types.copy()





def main():
    """Command line interface."""
    import os 
    pubmed_dir = "pubmed_txt"
    
    if not os.path.exists(pubmed_dir):
        print(f"Error: Directory '{pubmed_dir}' not found.")
        sys.exit(1)
    
    # Get all .txt files in the pubmed directory
    txt_files = [f for f in os.listdir(pubmed_dir) if f.endswith('.txt') and f != '.DS_Store']
    
    if not txt_files:
        print(f"No .txt files found in '{pubmed_dir}' directory.")
        return
    
    print(f"Found {len(txt_files)} .txt file(s) to process.\n")
    
    converter = PubMedToRISConverter()
    
    for file in txt_files:
        input_file = os.path.join(pubmed_dir, file)
        output_file = None  # Will auto-generate .ris filename
        
        try:
            print(f"Processing: {file}...")
            output_path = converter.convert_file(input_file, output_file)
            
            if output_path:
                print(f"✓ Successfully converted to: {output_path}\n")
            else:
                print(f"⚠ Warning: No output generated for {file}\n")
                
        except Exception as e:
            print(f"✗ Error processing {file}: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("Conversion process completed!")


if __name__ == "__main__":
    main()