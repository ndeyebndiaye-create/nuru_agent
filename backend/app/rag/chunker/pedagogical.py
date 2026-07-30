import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .config import ChunkerConfig

@dataclass
class PedagogicalChunk:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_type: str = "unknown"
    start_line: int = 0
    end_line: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "chunk_type": self.chunk_type,
            "metadata": self.metadata,
            "start_line": self.start_line,
            "end_line": self.end_line
        }

class PedagogicalChunker:
    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.patterns = {}
        for key, pattern_str in self.config.section_patterns.items():
            self.patterns[key] = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
        self.math_patterns = [re.compile(p, re.DOTALL) for p in self.config.math_patterns]
        self.remove_patterns = [re.compile(p, re.IGNORECASE) for p in self.config.remove_patterns]
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[PedagogicalChunk]:
        for pattern in self.remove_patterns:
            text = pattern.sub('', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        lines = text.split('\n')
        chunks = []
        current_type = "text"
        current_lines = []
        current_metadata = metadata.copy()
        
        for key, value in self.config.default_metadata.items():
            if key not in current_metadata:
                current_metadata[key] = value
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            detected_type = self._detect_section_type(line)
            
            if detected_type and detected_type not in ["text", "page_separator"]:
                if current_lines:
                    chunk_text = '\n'.join(current_lines)
                    if self._is_meaningful(chunk_text):
                        chunks.append(PedagogicalChunk(
                            text=chunk_text,
                            metadata=current_metadata.copy(),
                            chunk_type=current_type,
                            start_line=i - len(current_lines),
                            end_line=i - 1
                        ))
                
                current_type = detected_type
                current_lines = [line]
                current_metadata = metadata.copy()
                current_metadata["chunk_type"] = detected_type
                for key, value in self.config.default_metadata.items():
                    if key not in current_metadata:
                        current_metadata[key] = value
                i += 1
                continue
            
            if self._is_meaningful_line(line):
                current_lines.append(line)
            i += 1
        
        if current_lines:
            chunk_text = '\n'.join(current_lines)
            if self._is_meaningful(chunk_text):
                chunks.append(PedagogicalChunk(
                    text=chunk_text,
                    metadata=current_metadata.copy(),
                    chunk_type=current_type,
                    start_line=i - len(current_lines),
                    end_line=i - 1
                ))
        
        return self._enrich_chunks(chunks)
    
    def _detect_section_type(self, line: str) -> Optional[str]:
        if not line:
            return None
        # Nettoie les marqueurs Markdown d'emphase (gras/italique) en début
        # de ligne : les PDF extraits (Nougat/PyMuPDF) mettent très souvent
        # les mots-clés pédagogiques en gras, ex: "**Définition 1 :** ...".
        # Sans ce nettoyage, ces lignes ne matchaient jamais les patterns.
        cleaned = re.sub(r'^[\*_>\s]+', '', line).strip()
        for pattern_name, pattern in self.patterns.items():
            if pattern.match(cleaned):
                return pattern_name
        if re.match(r'^--- Page \d+ ---$', line):
            return "page_separator"
        return None
    
    def _is_meaningful_line(self, line: str) -> bool:
        if not line or line.isspace():
            return False
        if len(line.strip()) < 3:
            return False
        if re.match(r'^--- Page \d+ ---$', line.strip()):
            return False
        return True
    
    def _is_meaningful(self, text: str) -> bool:
        text = text.strip()
        if len(text) < self.config.min_chunk_size:
            return False
        return len(re.findall(r'\b\w+\b', text)) > 3
    
    def _enrich_chunks(self, chunks: List[PedagogicalChunk]) -> List[PedagogicalChunk]:
        for chunk in chunks:
            competences = self._extract_competences(chunk.text)
            if competences:
                chunk.metadata["competences"] = competences
            
            formula_count = 0
            for pattern in self.math_patterns:
                formula_count += len(pattern.findall(chunk.text))
            
            if formula_count > 0:
                chunk.metadata["has_formulas"] = True
                chunk.metadata["formula_count"] = formula_count
            
            chunk.metadata["difficulty_level"] = self._estimate_difficulty(chunk.text, formula_count)
            chunk.metadata["chunk_category"] = self.config.get_chunk_type_mapping().get(chunk.chunk_type, "course")
        
        return chunks
    
    def _extract_competences(self, text: str) -> List[str]:
        found = []
        text_lower = text.lower()
        for keyword in self.config.competence_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found[:5]
    
    def _estimate_difficulty(self, text: str, formula_count: int) -> str:
        length = len(text)
        for level, thresholds in self.config.difficulty_thresholds.items():
            if length <= thresholds["max_chars"] and formula_count <= thresholds["max_formulas"]:
                return level
        return "advanced"

class ChunkingPipeline:
    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()
        self.chunker = PedagogicalChunker(self.config)
    
    def process(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = self.chunker.chunk(text, metadata)
        chunks = [c for c in chunks if len(c.text.strip()) >= self.config.min_chunk_size]
        chunks = self._merge_small_chunks(chunks)
        chunks = self._split_large_chunks(chunks)
        return [c.to_dict() for c in chunks]
    
    def _merge_small_chunks(self, chunks: List[PedagogicalChunk]) -> List[PedagogicalChunk]:
        if not chunks:
            return chunks
        merged = []
        current = chunks[0]
        for i in range(1, len(chunks)):
            if len(current.text.strip()) < self.config.min_chunk_size:
                current.text += "\n\n" + chunks[i].text
                current.end_line = chunks[i].end_line
            else:
                merged.append(current)
                current = chunks[i]
        merged.append(current)
        return merged
    
    def _split_large_chunks(self, chunks: List[PedagogicalChunk]) -> List[PedagogicalChunk]:
        result = []
        for chunk in chunks:
            if len(chunk.text) <= self.config.max_chunk_size:
                result.append(chunk)
            else:
                paragraphs = chunk.text.split('\n\n')
                current_text = ""
                current_start = chunk.start_line
                for para in paragraphs:
                    if len(current_text) + len(para) <= self.config.max_chunk_size:
                        current_text += para + "\n\n"
                    else:
                        if current_text:
                            result.append(PedagogicalChunk(
                                text=current_text.strip(),
                                metadata=chunk.metadata.copy(),
                                chunk_type=chunk.chunk_type,
                                start_line=current_start,
                                end_line=chunk.end_line
                            ))
                            current_start = chunk.start_line
                        current_text = para + "\n\n"
                if current_text:
                    result.append(PedagogicalChunk(
                        text=current_text.strip(),
                        metadata=chunk.metadata.copy(),
                        chunk_type=chunk.chunk_type,
                        start_line=current_start,
                        end_line=chunk.end_line
                    ))
        return result