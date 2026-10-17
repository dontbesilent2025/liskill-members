#!/usr/bin/env python3
"""Copy the shared short-video structure library into the step 6-8 writing skills and build its index."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'structures'
FIELDS = ['脚本类型', '难度', '一句话适合', '必需素材', '呈现形式', '篇幅', '来源']
TYPES = ['干货', '过程', '故事', '情绪']
METHODS = ROOT / 'methods'
# Shared method notes and the skills that ship them.
METHOD_TARGETS = {
    '开头方法.md': ['li-script-opening', 'li-script-writing'],
    '四类脚本.md': ['li-script-form', 'li-script-writing'],
    '精修清单.md': ['li-script-writing'],
    '理论依据.md': ['li-script-form', 'li-script-opening', 'li-script-writing'],
}
INDEX_SKILLS = ['li-script-form', 'li-script-opening', 'li-script-writing']
COPY_SKILLS = INDEX_SKILLS
# Forms that already have their own skill: listed in the index, not duplicated in the library.
POINTERS = [
    ('城市印象反转', '情绪（辅：故事）', '讲一座城市的误解与真实体验，先误解后反转', '用户对这座城市的真实观察和反转经历', '`li-city-impressions`'),
    ('故事事件 Vlog 旁白', '故事', '一段真实经历或人物关系，写成克制、留白的旁白', '具体人物、事件和画面细节', '`li-story-vlog`'),
]


def structures():
    files = sorted(p for p in SOURCE.glob('*.md') if p.name != 'README.md')
    if not files:
        raise ValueError('结构库为空')
    return files


def info(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith(f'# {path.stem}\n'):
        raise ValueError(f'{path.name}: 标题必须与文件名一致')
    block = text.split('## 基本信息', 1)[1].split('\n## ', 1)[0] if '## 基本信息' in text else ''
    data = {}
    for key in FIELDS:
        match = re.search(rf'^- {key}：(.+)$', block, re.M)
        if not match:
            raise ValueError(f'{path.name}: 基本信息缺少「{key}」')
        data[key] = match.group(1).strip()
    main = data['脚本类型'].split('（', 1)[0]
    if main not in TYPES:
        raise ValueError(f'{path.name}: 脚本类型必须以 {"／".join(TYPES)} 之一开头')
    data['主类型'] = main
    return data


def cell(value):
    return value.replace('|', '／')


def index():
    rows = {t: [] for t in TYPES}
    for path in structures():
        d = info(path)
        rows[d['主类型']].append(f"| {path.stem} | {cell(d['脚本类型'])} | {cell(d['难度'])} | {cell(d['一句话适合'])} | {cell(d['必需素材'])} | {cell(d['呈现形式'])} |")
    lines = [
        '# 结构索引',
        '',
        '由仓库的结构库真源生成，请勿手改。按李同学的四类脚本分组：干货给收获感，过程留住时间、证明能力，故事建立人设和代入，情绪帮目标用户说话。第 6 步先定脚本类型，再在这一组里挑 2–3 个候选；完整结构在本技能的 references/structures 目录，文件名就是结构名。',
        '',
        f'共 {len(structures())} 个结构，另有 {len(POINTERS)} 种形式已有独立技能。',
    ]
    for t in TYPES:
        lines += ['', f'## {t}脚本', '', '| 结构 | 脚本类型 | 难度 | 一句话适合 | 必需素材 | 呈现形式 |', '|---|---|---|---|---|---|']
        lines += rows[t] or ['| （暂无） | | | | | |']
    lines += ['', '## 已有独立技能的形式', '', '选中这两种时，不在第 7、8 步写，直接转到对应技能。', '',
              '| 形式 | 脚本类型 | 一句话适合 | 必需素材 | 转到 |', '|---|---|---|---|---|']
    lines += [f'| {n} | {t} | {a} | {m} | {s} |' for n, t, a, m, s in POINTERS]
    return '\n'.join(lines) + '\n'


def expected():
    """Map of repo-relative path -> content for every generated file."""
    result = {}
    idx = index()
    for skill in INDEX_SKILLS:
        result[f'skills/{skill}/references/structure-index.md'] = idx
    for skill in COPY_SKILLS:
        for path in structures():
            result[f'skills/{skill}/references/structures/{path.name}'] = path.read_text(encoding='utf-8')
    for name, skills in METHOD_TARGETS.items():
        text = (METHODS / name).read_text(encoding='utf-8')
        for skill in skills:
            result[f'skills/{skill}/references/{name}'] = text
    return result


def stale():
    """Generated-looking files that no longer have a source."""
    wanted = set(expected())
    found = []
    for skill in COPY_SKILLS:
        for p in (ROOT / 'skills' / skill / 'references/structures').glob('*.md'):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in wanted:
                found.append(rel)
    return found


if __name__ == '__main__':
    for rel in stale():
        (ROOT / rel).unlink()
    for rel, content in expected().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    print(f'已生成 {len(structures())} 个结构副本和 {len(INDEX_SKILLS)} 份索引。')
