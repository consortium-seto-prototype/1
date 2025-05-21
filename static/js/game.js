
const config = {
    type: Phaser.AUTO,
    width: 350,
    height: 350,
    parent: 'game-container',
    scene: {
        preload: preload,
        create: createModeSelection,
        update: update
    }
};

const game = new Phaser.Game(config);

// キャンバス領域のcss
const style = document.createElement('style');
style.innerHTML = `
    #game-container {
        display: flex;
        justify-content: center;
        align-items: center;
        // height: 100vh;
        // background-color: #eee;
    }

    canvas {
        display: block;
    }
`;
document.head.appendChild(style);

let cardGrid = Array.from({ length: 3 }, () => Array(3).fill(null));
let currentPlayer = 1;
let playerScores = { 1: 0, 2: 0 };
let scoreText;
let currentPlayerText;
let remainingCard;
let gameMode = "normal";

function preload() {
    this.load.image('cardBack', 'static/images/game/card_spade_02.png');
    this.load.image('card1', 'static/images/game/card_heart_01.png');
    this.load.image('card3', 'static/images/game/card_heart_03.png');
    this.load.image('card4', 'static/images/game/card_heart_04.png');
    this.load.image('card5', 'static/images/game/card_heart_05.png');
}

function createModeSelection() {
    this.cameras.main.setBackgroundColor('#222');

    // 要素を中央に配置する
    let centerX = this.cameras.main.centerX;
    let centerY = this.cameras.main.centerY;

    // this.add.text(centerX, centerY, '中央', { fontSize: '32px' }).setOrigin(0.5);

    modeSelectionText = this.add.text(centerX, 100, 'モードを選択', { fontSize: '32px', fill: '#fff' }).setOrigin(0.5);

    let normalButton = this.add.text(centerX, 180, '1player', { fontSize: '28px', fill: '#fff' })
        .setInteractive()
        .on('pointerdown', () => startGame.call(this, "normal")).setOrigin(0.5);

    let hardButton = this.add.text(centerX, 260, '2player', { fontSize: '28px', fill: '#fff' })
        .setInteractive()
        .on('pointerdown', () => startGame.call(this, "hard")).setOrigin(0.5);

    // ボタンをクリック後に削除
    normalButton.on('pointerdown', () => {
        startGame.call(this, "normal");
        normalButton.destroy();
        hardButton.destroy();
        modeSelectionText.destroy();
    });

    hardButton.on('pointerdown', () => {
        startGame.call(this, "hard");
        normalButton.destroy();
        hardButton.destroy();
        modeSelectionText.destroy();
    });
}


function startGame(mode) {
    if (gameMode !== "normal" && gameMode !== "hard") return;  // モードが選択されていない場合は何もしない
    gameMode = mode;
    /*
     this.children.removeAll(); // モード選択画面を消す
    this.input.removeAllListeners();
    if (!cardGrid[0][0]) {  // cardGrid[0][0] が初期化されていなければカードを初期化
        initializeCards.call(this);
    }
    */
    //this.children.removeAll();

    create.call(this);
}


function create() {
    this.cameras.main.setBackgroundColor('#800000');
    console.log(currentPlayerText);
    if (!currentPlayerText) {  // 初回のみ作成
        console.log("yesssss")
        currentPlayerText = this.add.text(20, 315, `プレイヤー: ${currentPlayer}`, { fontSize: '15px', fill: '#fff' });
    }
    if (!scoreText) {  // 初回のみ作成
        scoreText = this.add.text(180, 315, `スコア P1: ${playerScores[1]} P2: ${playerScores[2]}`, { fontSize: '15px', fill: '#fff' });
    }
    if (!cardGrid[0][0]) {
        initializeCards.call(this);
    }
    updateDisplay.call(this);
}


function initializeCards() {

    console.log("cardshuffle");

    const cardValues = [
        { value: 1, count: 4 }, { value: 3, count: 3 },
        { value: 4, count: 2 }, { value: 5, count: 1 }
    ];

    let cardList = [];
    const backValue = 2;

    cardValues.forEach(({ value, count }) => {
        for (let i = 0; i < count; i++) {
            // カードオブジェクトに clicked フラグを追加
            cardList.push({ value, isFaceUp: false, backValue: backValue, clicked: false });
        }
    });

    Phaser.Utils.Array.Shuffle(cardList);

    const selectedCards = cardList.slice(0, 9);
    const lastCard = cardList[9];

    let positions = [];
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            positions.push({ row: i, col: j });
        }
    }
    Phaser.Utils.Array.Shuffle(positions);

    for (let i = 0; i < 9; i++) {
        let { row, col } = positions[i];

        let card = this.add.image(300, 350, 'cardBack')
            .setInteractive()
            .setDisplaySize(60, 90);

        // カードに clicked フラグをセット
        card.value = selectedCards[i].value;
        card.isFaceUp = false;
        card.backValue = backValue;
        card.row = row;
        card.col = col;
        card.clicked = false;  // clicked フラグを初期化
        card.on('pointerdown', () => selectCard.call(this, card));
        cardGrid[row][col] = card;

        //card.setPosition(100 + col * 150, 100 + row * 150);

        this.tweens.add({
            targets: card,
            x: 45 + col * 90,
            y: 55 + row * 100,
            duration: 500,
            delay: i * 100,
            ease: 'Power2'
        });
    }

    remainingCard = this.add.image(305, 60, 'cardBack')
        .setDisplaySize(65, 95);
    remainingCard.value = lastCard.value;
    remainingCard.isFaceUp = false;
    remainingCard.backValue = backValue;
    flipCard(remainingCard);

    console.log(cardList);
    console.log(cardGrid);

}

function selectCard(card) {
    console.log(cardGrid);

    if (card.clicked) return;

    console.log(card.clicked);

    card.clicked = true;

    console.log(card.clicked);


    let points = card.isFaceUp ? card.value : card.backValue;

    if (card.isFaceUp && card.value === remainingCard.value) {
        points = -points;
    }

    playerScores[currentPlayer] += points;

    //flipCard(card);  // ここでカードをひっくり返す
    changePlayer();
    updateDisplay();

    flipAdjacentCards(card.row, card.col);

    cardGrid[card.row][card.col] = null;

    // カード削除
    card.destroy();

    // ゲーム終了
    if (checkGameOver()) {
        endGame.call(this);
    }
}


function flipCard(card) {
    card.isFaceUp = !card.isFaceUp;
    const texture = card.isFaceUp ? `card${card.value}` : 'cardBack';
    card.setTexture(texture);
}

function flipAdjacentCards(row, col) {
    const directions = [
        { dr: -1, dc: 0 }, { dr: 1, dc: 0 },
        { dr: 0, dc: -1 }, { dr: 0, dc: 1 }
    ];

    directions.forEach(({ dr, dc }) => {
        const adjacentRow = row + dr;
        const adjacentCol = col + dc;

        // 隣接カードがグリッドの範囲内か確認
        if (adjacentRow >= 0 && adjacentRow < 3 && adjacentCol >= 0 && adjacentCol < 3) {
            const adjacentCard = cardGrid[adjacentRow][adjacentCol];
            if (adjacentCard) {
                flipCard(adjacentCard);
            }
        }
    });
}


function changePlayer() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
}

function updateDisplay() {
    currentPlayerText.setText(`プレイヤー: ${currentPlayer}`);
    scoreText.setText(`スコア P1: ${playerScores[1]} P2: ${playerScores[2]}`);
}



function checkGameOver() {
    return cardGrid.every(row => row.every(card => card === null));
}

function endGame() {
    // 要素を中央に配置する
    let centerX = this.cameras.main.centerX;
    let centerY = this.cameras.main.centerY;

    let winner = playerScores[1] > playerScores[2] ? 'プレイヤー 1' :
        playerScores[1] < playerScores[2] ? 'プレイヤー 2' : '引き分け';

    // 勝者テキストを追加
    this.add.text(centerX, 100, `Win: ${winner}`, { fontSize: '32px', fill: '#fff' }).setOrigin(0.5);

    // remainingCardを削除
    if (remainingCard) {
        remainingCard.destroy();
    }

    // モード選択に戻るボタン
    let menuButton = this.add.text(centerX, 180, 'モード選択に戻る', { fontSize: '28px', fill: '#fff', backgroundColor: '#444' })
        .setInteractive()
        .on('pointerdown', () => {
            this.children.removeAll();  // 現在のシーンを再読み込みし、初期状態に戻す
            playerScores = { 1: 0, 2: 0 }; // スコアリセット
            currentPlayer = 1;
            scoreText = null;
            currentPlayerText = null;
            cardGrid = Array.from({ length: 3 }, () => Array(3).fill(null)); // カードを初期化
            this.children.removeAll();
            createModeSelection.call(this); // モード選択画面を表示
        }).setOrigin(0.5);

    // もう一度遊ぶボタン
    let replayButton = this.add.text(centerX, 260, 'もう一度遊ぶ', { fontSize: '28px', fill: '#fff', backgroundColor: '#444' })
        .setInteractive()
        .on('pointerdown', () => {
            resetGame.call(this); // ゲームの状態をリセットして再スタート
        }).setOrigin(0.5);
}




function resetGame() {
    playerScores = { 1: 0, 2: 0 }; // スコアリセット
    currentPlayer = 1;            // プレイヤーを初期化
    cardGrid = Array.from({ length: 3 }, () => Array(3).fill(null)); // カードを初期化
    this.children.removeAll();    // シーン内のオブジェクトをすべて削除

    // スコア表示を再作成
    scoreText = this.add.text(180, 315, `スコア P1: ${playerScores[1]} P2: ${playerScores[2]}`, { fontSize: '15px', fill: '#fff' });
    currentPlayerText = this.add.text(20, 315, `プレイヤー: ${currentPlayer}`, { fontSize: '15px', fill: '#fff' });

    create.call(this); // ゲームを再度開始
}


function update() { }
