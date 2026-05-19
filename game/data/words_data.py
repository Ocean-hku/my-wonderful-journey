"""游戏所有词汇数据及场景配置"""

# ── 超市8件采购物品 ─────────────────────────────────────────────
SHOPPING_ITEMS = [
    {
        "word": "backpack",
        "zh": "背包",
        "image": "6背包拼写.PNG",
        "challenge_img": "22背包.PNG",
        "challenge_img_adv": "22背包高级.PNG",
        "word_audio": "word/backpack.mp3",
        "intro_audio": {
            "dad": "2采购清单/采购清单-父母介绍/清单背包 父.mp3",
            "mom": "2采购清单/采购清单-父母介绍/清单背包 母.mp3",
        },
    },
    {
        "word": "apple",
        "zh": "苹果",
        "image": "6苹果拼写.PNG",
        "challenge_img": "22苹果.PNG",
        "challenge_img_adv": "22苹果高级.PNG",
        "word_audio": "word/apple.mp3",
        "intro_audio": {
            "mom": "2采购清单/采购清单-父母介绍/清单苹果 母.mp3",
        },
    },
    {
        "word": "bandage",
        "zh": "创可贴",
        "image": "6创可贴拼写.PNG",
        "challenge_img": "22创可贴.PNG",
        "challenge_img_adv": "22创可贴高级.PNG",
        "word_audio": "word/bandage.mp3",
        "intro_audio": {
            "mom": "2采购清单/采购清单-父母介绍/清单创可贴 母.mp3",
        },
    },
    {
        "word": "bottle",
        "zh": "水壶",
        "image": "6水壶拼写.PNG",
        "challenge_img": "22水壶.PNG",
        "challenge_img_adv": "22水壶高级.PNG",
        "word_audio": "word/bottle.mp3",
        "intro_audio": {
            "dad": "2采购清单/采购清单-父母介绍/清单水壶 父.mp3",
            "mom": "2采购清单/采购清单-父母介绍/清单水壶 母.mp3",
        },
    },
    {
        "word": "cake",
        "zh": "蛋糕",
        "image": "6蛋糕拼写.PNG",
        "challenge_img": "22蛋糕.PNG",
        "challenge_img_adv": "22蛋糕高级.PNG",
        "word_audio": "word/cake.mp3",
        "intro_audio": {
            "mom": "2采购清单/采购清单-父母介绍/清单蛋糕 母.mp3",
        },
    },
    {
        "word": "compass",
        "zh": "指南针",
        "image": "6指南针拼写.PNG",
        "challenge_img": "22指南针.PNG",
        "challenge_img_adv": "22指南针高级.PNG",
        "word_audio": "word/compass.mp3",
        "intro_audio": {
            "dad": "2采购清单/采购清单-父母介绍/清单指南针 父.mp3",
            "mom": "2采购清单/采购清单-父母介绍/清单指南针 母.mp3",
        },
    },
    {
        "word": "lollipop",
        "zh": "棒棒糖",
        "image": "6棒棒糖拼写.PNG",
        "challenge_img": "22棒棒糖.PNG",
        "challenge_img_adv": "22棒棒糖高级.PNG",
        "word_audio": "word/lollipop.mp3",
        "intro_audio": {
            "mom": "2采购清单/采购清单-父母介绍/清单棒棒糖 母.mp3",
        },
    },
    {
        "word": "umbrella",
        "zh": "雨伞",
        "image": "6雨伞拼写.PNG",
        "challenge_img": "22雨伞.PNG",
        "challenge_img_adv": "22雨伞高级.PNG",
        "word_audio": "word/umbrella.mp3",
        "intro_audio": {
            "dad": "2采购清单/采购清单-父母介绍/清单雨伞 父.mp3",
            "mom": "2采购清单/采购清单-父母介绍/清单雨伞 母.mp3",
        },
    },
]

# ── 森林9只动物 ──────────────────────────────────────────────────
FOREST_ANIMALS = [
    {
        "word": "fox",
        "zh": "狐狸",
        "frames": ["12狐狸1.PNG", "12狐狸2.PNG", "12狐狸3.PNG", "12狐狸4.PNG"],
        "challenge_img": "22狐狸.PNG",
        "challenge_img_adv": "22狐狸高级.PNG",
        "word_audio": "word/fox.mp3",
        "handbook_audio": "4森林动物手册/手册狐狸 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互狐狸 父.mp3",
            "mom": "5森林动物交互/交互狐狸 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/005_狐狸_我只是好奇里面有什么.mp3",
            "5森林动物交互/006_狐狸_这个包真酷还给你.mp3",
        ],
    },
    {
        "word": "horse",
        "zh": "小马",
        "frames": ["13小马1.PNG", "13小马2.PNG", "13小马3.PNG"],
        "challenge_img": "22小马.PNG",
        "challenge_img_adv": "22小马高级.PNG",
        "word_audio": "word/horse.mp3",
        "handbook_audio": "4森林动物手册/手册马 父.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互小马 父.mp3",
            "mom": "5森林动物交互/交互小马 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/009_小马_谢谢你的苹果.mp3",
            "5森林动物交互/010_小马_真甜啊想不想骑着我.mp3",
        ],
    },
    {
        "word": "pig",
        "zh": "小猪",
        "frames": ["14小猪1.PNG", "14小猪2.PNG", "14小猪3.PNG"],
        "challenge_img": "22小猪.PNG",
        "challenge_img_adv": "22小猪高级.PNG",
        "word_audio": "word/pig.mp3",
        "handbook_audio": "4森林动物手册/手册小猪 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互小猪 父.mp3",
            "mom": "5森林动物交互/交互小猪 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/016_小猪_蛋糕是世界上最美味的.mp3",
            "5森林动物交互/017_小猪_从现在起我们就是最好.mp3",
        ],
    },
    {
        "word": "sheep",
        "zh": "小羊",
        "frames": ["15小羊1.PNG", "15小羊2.PNG", "15小羊3.PNG"],
        "challenge_img": "22小羊.PNG",
        "challenge_img_adv": "22小羊高级.PNG",
        "word_audio": "word/sheep.mp3",
        "handbook_audio": "4森林动物手册/手册小羊 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互小羊 父.mp3",
            "mom": "5森林动物交互/交互小羊 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/022_小羊_水真好喝谢谢你.mp3",
            "5森林动物交互/023_小羊_你是我遇到的最善良的.mp3",
        ],
    },
    {
        "word": "elephant",
        "zh": "大象",
        "frames": ["16大象1.PNG", "16大象2.PNG", "16大象3.PNG"],
        "challenge_img": "22大象.PNG",
        "challenge_img_adv": "22大象高级.PNG",
        "word_audio": "word/elephant.mp3",
        "handbook_audio": "4森林动物手册/手册大象 父.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互大象 父.mp3",
            "mom": "5森林动物交互/交互大象 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/028_大象_对不起喷到你了吗.mp3",
            "5森林动物交互/029_大象_幸好你带了雨伞.mp3",
        ],
    },
    {
        "word": "tiger",
        "zh": "老虎",
        "frames": ["17老虎1.PNG", "17老虎2.PNG", "17老虎3.PNG"],
        "challenge_img": "22老虎.PNG",
        "challenge_img_adv": "22老虎高级.PNG",
        "word_audio": "word/tiger.mp3",
        "handbook_audio": "4森林动物手册/手册老虎 父.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互老虎 父.mp3",
            "mom": "5森林动物交互/交互老虎 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/035_老虎_吼谢谢你的创可贴.mp3",
            "5森林动物交互/036_老虎_有我在这片森林里.mp3",
        ],
    },
    {
        "word": "parrot",
        "zh": "鹦鹉",
        "frames": ["18鹦鹉1.PNG", "18鹦鹉2.PNG", "18鹦鹉3.PNG"],
        "challenge_img": "22鹦鹉.PNG",
        "challenge_img_adv": "22鹦鹉高级.PNG",
        "word_audio": "word/parrot.mp3",
        "handbook_audio": "4森林动物手册/手册鹦鹉 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互鹦鹉 父.mp3",
            "mom": "5森林动物交互/交互鹦鹉 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/042_鹦鹉_亮晶晶.mp3",
            "5森林动物交互/043_鹦鹉_好玩.mp3",
            "5森林动物交互/044_鹦鹉_还给你啦.mp3",
            "5森林动物交互/045_鹦鹉_哎呀卡在树上了让.mp3",
        ],
    },
    {
        "word": "giraffe",
        "zh": "长颈鹿",
        "frames": ["19长颈鹿1.PNG", "19长颈鹿2.PNG", "19长颈鹿3.PNG"],
        "challenge_img": "22长颈鹿.PNG",
        "challenge_img_adv": "22长颈鹿高级.PNG",
        "word_audio": "word/giraffe.mp3",
        "handbook_audio": "4森林动物手册/手册长颈鹿 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互长颈鹿 父.mp3",
            "mom": "5森林动物交互/交互长颈鹿 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/050_长颈鹿_这点高度不算什么.mp3",
            "5森林动物交互/051_长颈鹿_喏别再弄丢啦.mp3",
        ],
    },
    {
        "word": "monkey",
        "zh": "猴子",
        "frames": ["20猴子1.PNG", "20猴子2.PNG", "20猴子3.PNG"],
        "challenge_img": "22猴子.PNG",
        "challenge_img_adv": "22猴子高级.PNG",
        "word_audio": "word/monkey.mp3",
        "handbook_audio": "4森林动物手册/手册猴子 母.mp3",
        "interact_audio": {
            "dad": "5森林动物交互/交互猴子 父.mp3",
            "mom": "5森林动物交互/交互猴子 母.mp3",
        },
        "animal_lines": [
            "5森林动物交互/055_猴子_欢迎来森林玩.mp3",
            "5森林动物交互/056_猴子_你真厉害.mp3",
        ],
    },
]

# 所有17个词（挑战模式用）
ALL_WORDS = SHOPPING_ITEMS + FOREST_ANIMALS
