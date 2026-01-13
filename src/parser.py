"""Skill 文件解析器"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .types import Script


class SkillParser:
    """解析 Agent Skills (SKILL.md 格式)"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.config: Optional[Dict] = None
        self.scripts: List[str] = []
        self.scripts_with_metadata: List[Tuple[str, str, int]] = []  # (content, language, line_offset)
        self.markdown_content: str = ""

    def parse(self) -> bool:
        """解析 skill 目录"""
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill 路径不存在: {self.skill_path}")

        # 查找 SKILL.md
        skill_file = self.skill_path / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"未找到 SKILL.md 文件: {self.skill_path}")

        # 解析 SKILL.md
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 frontmatter 和主体内容
        self._parse_frontmatter(content)
        self._extract_code_blocks(content)
        self._extract_scripts_from_directory()

        return True

    def _parse_frontmatter(self, content: str):
        """解析 YAML frontmatter"""
        # 匹配 --- ... --- 之间的内容
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if match:
            frontmatter_text = match.group(1)
            self.markdown_content = match.group(2)
            self.config = yaml.safe_load(frontmatter_text)
        else:
            self.markdown_content = content

    def _extract_code_blocks(self, content: str):
        """从 Markdown 中提取代码块"""
        # 匹配 ```language 代码块，捕获语言和内容
        pattern = r'```(python|javascript|bash|sh)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)

        for language, code in matches:
            self.scripts.append(code)
            # 计算行偏移（简化版：不精确计算，设为 0）
            # 实际应用中可以通过查找代码在原文中的位置来计算
            lang_normalized = 'shell' if language in ['bash', 'sh'] else language
            self.scripts_with_metadata.append((code, lang_normalized, 0))

    def _extract_scripts_from_directory(self):
        """从 scripts/ 目录提取脚本文件"""
        scripts_dir = self.skill_path / "scripts"
        if scripts_dir.exists() and scripts_dir.is_dir():
            for script_file in scripts_dir.glob("*"):
                if script_file.is_file() and script_file.suffix in ['.sh', '.bash', '.py', '.js']:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.scripts.append(content)
                        # 根据文件扩展名检测语言
                        language = self._detect_language_from_extension(script_file.suffix)
                        self.scripts_with_metadata.append((content, language, 0))

    def get_all_scripts(self) -> List[str]:
        """获取所有脚本内容"""
        return self.scripts

    def _detect_language_from_extension(self, extension: str) -> str:
        """根据文件扩展名检测语言

        Args:
            extension: 文件扩展名（如 '.py'）

        Returns:
            语言名称
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.sh': 'shell',
            '.bash': 'shell',
        }
        return extension_map.get(extension, 'unknown')

    def get_all_scripts_with_metadata(self) -> List[Script]:
        """获取所有脚本及其元数据

        Returns:
            Script 对象列表
        """
        scripts = []
        for content, language, line_offset in self.scripts_with_metadata:
            scripts.append(Script(
                content=content,
                language=language,
                source='markdown' if line_offset == 0 else 'file',
                line_offset=line_offset
            ))
        return scripts
