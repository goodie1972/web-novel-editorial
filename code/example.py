# -*- coding: utf-8 -*-
"""
Chroma 长记忆系统使用示例
展示如何将 Chroma 集成到网文撰写工作流
"""

from chroma_writer import ChromaWriter, ChromaUpdater
from chroma_reader import ChromaReader, ContextBuilder

# ========== 示例1: 初始化项目数据 ==========


def init_project():
    """初始化项目时调用"""
    writer = ChromaWriter("./chroma_data")

    # 1. 写入世界观设定
    world_settings = [
        {
            "name": "等级体系",
            "content": "超能力等级：F→E→D→C→B→A→S→SS→SSS，每级分初期、中期、后期、巅峰",
            "category": "level",
        },
        {
            "name": "势力分布",
            "content": "华夏超管局（官方）、五大宗门（正派）、黑暗议会（反派）、隐世家族（中立）",
            "category": "faction",
        },
        {
            "name": "地理设定",
            "content": "主要城市：江城（主角活动范围）、燕京（超管局总局）、昆仑（秘境所在地）",
            "category": "geography",
        },
    ]

    for setting in world_settings:
        writer.add_world_setting(
            content=setting["content"],
            name=setting["name"],
            category=setting["category"],
        )

    # 2. 写入人物设定
    characters = [
        {
            "name": "叶尘",
            "content": "主角，18岁，江城大学学生。性格杀伐果断，人不犯我我不犯人。金手指：超能进化系统（时空之刃）。目标：变强保护妹妹",
            "chapter": 1,
            "role": "主角",
        },
        {
            "name": "林诗雨",
            "content": "女主/妹妹，17岁，江城大学附属中学学生。活泼可爱，表面大大咧咧实际关心哥哥。隐藏血脉：青龙血脉（后续觉醒）",
            "chapter": 1,
            "role": "女主",
        },
        {
            "name": "苏雨晴",
            "content": "女配，校花，天才少女。冷傲性格，前期对手后期暧昧。身份：苏家千金，修炼天赋极高",
            "chapter": 3,
            "role": "女配",
        },
        {
            "name": "王腾",
            "content": "反派，豪门大少，B级实力。与主角作对，结局被击败。性格跋扈，仗势欺人",
            "chapter": 5,
            "role": "反派",
        },
    ]

    for char in characters:
        writer.add_character(
            name=char["name"],
            content=char["content"],
            chapter=char["chapter"],
            role=char["role"],
        )

    # 3. 写入技能设定
    skills = [
        {
            "name": "时空之刃",
            "content": "主角核心技能，S级，可进化。能力：空间切割、时间静止。进化路线：时空之刃→时空领域→时空破碎",
            "category": "核心技能",
            "owner": "叶尘",
        }
    ]

    for skill in skills:
        writer.add_skill(
            name=skill["name"],
            content=skill["content"],
            category=skill["category"],
            owner=skill["owner"],
        )

    # 4. 写入伏笔
    foreshadowing = [
        {
            "name": "妹妹血脉",
            "content": "林诗雨体内隐藏青龙血脉，危机时刻会觉醒，觉醒后实力远超同级",
            "embed_chapter": 1,
            "recover_chapter": 30,
        },
        {
            "name": "黑暗阴谋",
            "content": "黑暗议会暗中进行深渊之门计划，企图统治世界",
            "embed_chapter": 10,
            "recover_chapter": 50,
        },
    ]

    for fs in foreshadowing:
        writer.add_foreshadowing(
            name=fs["name"],
            content=fs["content"],
            embed_chapter=fs["embed_chapter"],
            recover_chapter=fs["recover_chapter"],
        )

    print("项目数据初始化完成！")


# ========== 示例2: 章节完成后写入 ==========


def on_chapter_complete(chapter_num, chapter_content, summary):
    """章节完成后调用"""
    writer = ChromaWriter("./chroma_data")
    updater = ChromaUpdater("./chroma_data")

    # 1. 写入章节摘要
    summary_text = f"""
    第{chapter_num}章：{summary["title"]}
    核心事件：{summary["main_event"]}
    出场人物：{summary["characters"]}
    爽点：{summary["happy_point"]}
    钩子：{summary["hook"]}
    """

    writer.add_chapter_summary(
        chapter_num=chapter_num,
        content=summary_text,
        metadata={
            "title": summary["title"],
            "main_event": summary["main_event"],
            "word_count": summary.get("word_count", 2500),
        },
    )

    # 2. 写入本章埋设的伏笔
    for fs in summary.get("new_foreshadowing", []):
        writer.add_foreshadowing(
            name=fs["name"],
            content=fs["content"],
            embed_chapter=chapter_num,
            recover_chapter=fs["planned_recover"],
        )

    # 3. 标记已回收的伏笔
    for fs_name in summary.get("recovered_foreshadowing", []):
        updater.recover_foreshadowing(fs_name, chapter_num)

    print(f"第{chapter_num}章已存入向量数据库")


# ========== 示例3: 写作前查询 ==========


def on_before_write(chapter_num):
    """写手开始写作前调用"""
    builder = ContextBuilder("./chroma_data")
    context = builder.build_write_context(chapter_num)

    print(f"\n{'=' * 50}")
    print(f"开始写作第{chapter_num}章")
    print(f"{'=' * 50}")

    # 显示最近章节
    print("\n【最近章节】")
    for ch in context["recent_chapters"]:
        print(f"  - {ch['metadata'].get('title', 'N/A')}: {ch['document'][:50]}...")

    # 显示本章出场人物
    print("\n【本章出场人物】")
    for char in context["characters_appearing"]:
        print(f"  - {char['metadata']['name']} ({char['metadata']['role']})")

    # 显示相关伏笔
    print("\n【相关伏笔】")
    for fs in context["foreshadowing"]:
        status = "埋入" if fs["metadata"]["embed_chapter"] == chapter_num else "回收"
        print(f"  - [{status}] {fs['metadata']['name']}: {fs['document']}")

    # 显示活跃伏笔
    print("\n【需要记住的伏笔】")
    for fs in context["active_foreshadowing"]:
        print(
            f"  - {fs['metadata']['name']} (第{fs['metadata']['embed_chapter']}章埋入，计划{fs['metadata']['recover_chapter']}章回收)"
        )

    return context


# ========== 示例4: 审核时查询 ==========


def on_review(chapter_num):
    """编辑审核时调用"""
    builder = ContextBuilder("./chroma_data")
    context = builder.build_review_context(chapter_num)

    print(f"\n{'=' * 50}")
    print(f"审核第{chapter_num}章")
    print(f"{'=' * 50}")

    # 显示所有人物设定（用于核对一致性）
    print("\n【人物设定参考】")
    if context["all_characters"] and context["all_characters"]["documents"]:
        for i, doc in enumerate(context["all_characters"]["documents"]):
            meta = context["all_characters"]["metadatas"][i]
            print(f"  - {meta['name']} ({meta['role']}): {doc[:50]}...")

    # 显示相关伏笔
    print("\n【伏笔状态】")
    for fs in context["foreshadowing"]:
        print(f"  - {fs['metadata']['name']}: {fs['document']}")

    return context


# ========== 运行示例 ==========

if __name__ == "__main__":
    # 1. 初始化项目（首次运行）
    # init_project()

    # 2. 写作前查询
    context = on_before_write(11)

    # 3. 章节完成后写入
    # on_chapter_complete(10, "章节内容...", {
    #     "title": "突破B级",
    #     "main_event": "主角突破到B级",
    #     "characters": "叶尘、林诗雨",
    #     "happy_point": "越级突破",
    #     "hook": "突然收到神秘消息",
    #     "new_foreshadowing": [],
    #     "recovered_foreshadowing": []
    # })

    # 4. 审核时查询
    # on_review(10)
