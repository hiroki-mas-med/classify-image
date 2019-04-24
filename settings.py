class Settings:
    """
    調整すべき設定の集合
    """

    # k-Fold法の分割数を指定
    # 基本的にはk=5で良いと思います
    # hold out法を使用する場合は K=1 とすること
    K = 5

    # PIC_MODE: 解析のモードを指定
    # PIC_MODE = 0: 2値分類
    # 解析結果
    #   AUC、感度・特異度
    #
    # PIC_MODE = 1: 多クラス分類
    # 解析結果
    #   正答率のみ
    #
    # PIC_MODE = 2: 回帰
    # データセットの準備
    #   imgフォルダに適当な名前("_"禁止)で1フォルダだけ作成し、その中にすべての画像を入れる
    #   画像のファイル名は"{ターゲット}_{元々のファイル名}"に修正しておく
    PIC_MODE = 1

    # バッチサイズを指定
    # 重たい時には少なくしてください。
    BATCH_SIZE = 32

    # data拡張の際(ImageDataGenerator)の引数を指定(基本的にそのままで良い)
    ROTATION_RANGE = 2
    WIDTH_SHIFT_RANGE = 0.01
    HEIGHT_SHIFT_RANGE = 0.01
    SHEAR_RANGE = 0
    ZOOM_RANGE = 0.1

    # data拡張のオプション
    NUM_OF_AUGS = 5  # 1-9で指定。9種類の中からランダムに(NUM_OF_AUGS)種類の処理を行う。
    USE_FLIP = True  # Falseなら左右反転無し、Trueなら左右反転してデータ数を２倍にする。

    # 各種フォルダ名指定(基本的にそのままで良い)
    IMG_ROOT = "img"  # 画像のフォルダ
    DATASET_FOLDER = "dataset"  # 分割したデータのファイル名が記載されたcsvファイルのフォルダ
    TRAIN_ROOT = "train"  # 訓練用画像が出力されるフォルダ (解析終了後は削除される)
    TEST_ROOT = "test"  # 評価用画像が出力されるフォルダ (解析終了後は削除される)

    # 解析に使うモデルのネットワーク構造の指定
    # 例えば、VGG16とVGG19で解析するならば、["VGG16", "VGG19"]みたいにしてください。
    # 以下は現時点で実装されているネットワーク構造を全て使った例
    # OUTPUT_FOLDER_LIST = ["VGG16","VGG19","DenseNet121","DenseNet169","DenseNet201",
    #                       "InceptionResNetV2","InceptionV3","ResNet50","Xception"]
    OUTPUT_FOLDER_LIST = ["VGG16"]

    # 画像サイズ(解像度)の指定
    IMG_SIZE = [224, 224]

    # エポック数の指定
    EPOCHS = 20

    # 統計解析の信頼区間を指定
    ALPHA = 0.95

    # colabとdriveの同期を待つ時間(秒単位)
    # ローカルでこのコードを実行する場合、待つ必要はないので0を推奨
    WAITSEC = 120

    def __init__(self):
        pass