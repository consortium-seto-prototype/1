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
let turnOfCpu = false;
let playerScores = { 1: 0, 2: 0 };
let scoreText;
let currentPlayerText;
let remainingCard;
let gameMode = "player_1";
let senkou = false;
let manageCreate = true;

function preload() {
    this.load.image('cardBack', 'static/images/game/card_spade_02.png');
    this.load.image('card1', 'static/images/game/card_heart_01.png');
    this.load.image('card3', 'static/images/game/card_heart_03.png');
    this.load.image('card4', 'static/images/game/card_heart_04.png');
    this.load.image('card5', 'static/images/game/card_heart_05.png');
    this.load.image('cardBack_selected', 'static/images/game/card_spade_02_selected.png');
    this.load.image('card1_selected', 'static/images/game/card_heart_01_selected.png'); // 彩度を落とした画像を追加
    this.load.image('card3_selected', 'static/images/game/card_heart_03_selected.png');
    this.load.image('card4_selected', 'static/images/game/card_heart_04_selected.png');
    this.load.image('card5_selected', 'static/images/game/card_heart_05_selected.png');
}

function createModeSelection() {
    this.cameras.main.setBackgroundColor('#222');

    let centerX = this.cameras.main.centerX;
    let centerY = this.cameras.main.centerY;

    let modeSelectionText = this.add.text(centerX - 90, centerY - 100, 'モードを選択', { fontSize: '24px', fill: '#fff', padding: { top: 10, bottom: 10 } });

    let oneP_Button = this.add.text(centerX - 65, centerY - 50, '1人で遊ぶ', { fontSize: '20px', fill: '#fff', padding: { top: 10, bottom: 10 } })
        .setInteractive()
        .on('pointerdown', () => createTurnSelection.call(this));

    let twoP_Button = this.add.text(centerX - 65, centerY, '2人で遊ぶ', { fontSize: '20px', fill: '#fff', padding: { top: 10, bottom: 10 } })
        .setInteractive()
        .on('pointerdown', () => startGame.call(this, "player_2"));

    oneP_Button.on('pointerdown', () => {
        createTurnSelection.call(this);
        oneP_Button.destroy();
        twoP_Button.destroy();
        modeSelectionText.destroy();
    });

    twoP_Button.on('pointerdown', () => {
        startGame.call(this, "player_2");
        oneP_Button.destroy();
        twoP_Button.destroy();
        modeSelectionText.destroy();
    });
}

function createTurnSelection() {
    if (senkou) return;

    this.cameras.main.setBackgroundColor('#222');

    let centerX = this.cameras.main.centerX;
    let centerY = this.cameras.main.centerY;

    let turnSelectionText = this.add.text(centerX - 90, centerY - 100, '先攻後攻を選択', { fontSize: '24px', fill: '#fff', padding: { top: 10, bottom: 10 } });

    let firstTurnButton = this.add.text(centerX - 65, centerY - 50, '先攻', { fontSize: '20px', fill: '#fff', padding: { top: 10, bottom: 10 } })
        .setInteractive()
        .on('pointerdown', () => startGame.call(this, "player_1", true));

    let secondTurnButton = this.add.text(centerX - 65, centerY, '後攻', { fontSize: '20px', fill: '#fff', padding: { top: 10, bottom: 10 } })
        .setInteractive()
        .on('pointerdown', () => startGame.call(this, "player_1", false));

    firstTurnButton.on('pointerdown', () => {
        startGame.call(this, "player_1", true);
        firstTurnButton.destroy();
        secondTurnButton.destroy();
        turnSelectionText.destroy();
    });

    secondTurnButton.on('pointerdown', () => {
        startGame.call(this, "player_1", false);
        firstTurnButton.destroy();
        secondTurnButton.destroy();
        turnSelectionText.destroy();
    });

    senkou = true;
}

function startGame(mode, isFirstTurn = true) {
    if (gameMode !== "player_1" && gameMode !== "player_2") return;
    gameMode = mode;
    currentPlayer = isFirstTurn ? 1 : 2; // 選択に基づいて開始プレイヤーを設定

    // 1人プレイの場合の名前設定
    if (gameMode === "player_1") {
        playerNames = isFirstTurn ? { 1: "you", 2: "cpu" } : { 1: "cpu", 2: "you" };
        console.log(playerNames);
    } else {
        playerNames = { 1: "1P", 2: "2P" };
    }

    if (manageCreate) create.call(this);

    // 後攻が選ばれた場合、CPUのターンを先に実行
    if (gameMode === "player_1" && !isFirstTurn && manageCreate) {
        cpuTurn.call(this);
    }
    manageCreate = false;
}




function create() {
    this.cameras.main.setBackgroundColor('#800000');
    if (!currentPlayerText) { // 初回のみ作成
        currentPlayerText = this.add.text(10, 310, `プレイヤー: ${currentPlayer}`, { fontSize: '16px', fill: '#fff', padding: { top: 10, bottom: 10 } });
    }
    if (!scoreText) { // 初回のみ作成
        scoreText = this.add.text(160, 310, `得点 P1: ${playerScores[1]} P2: ${playerScores[2]}`, { fontSize: '16px', fill: '#fff', padding: { top: 10, bottom: 10 } });
    }
    if (!cardGrid[0][0]) {
        initializeCards.call(this);
    }
    updateDisplay.call(this);
}

function initializeCards() {
    const cardValues = [
        { value: 1, count: 4 }, { value: 3, count: 3 },
        { value: 4, count: 2 }, { value: 5, count: 1 }
    ];

    let cardList = [];
    const backValue = 2;

    cardValues.forEach(({ value, count }) => {
        for (let i = 0; i < count; i++) {
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

        let card = this.add.image(175, 175, 'cardBack')
            .setInteractive()
            .setDisplaySize(70, 100);

        card.value = selectedCards[i].value;
        card.isFaceUp = false;
        card.backValue = backValue;
        card.row = row;
        card.col = col;
        card.clicked = false;
        card.on('pointerdown', () => selectCard.call(this, card));
        cardGrid[row][col] = card;

        this.tweens.add({
            targets: card,
            x: 50 + col * 100,
            y: 50 + row * 100,
            duration: 500,
            delay: i * 100,
            ease: 'Power2'
        });
    }

    remainingCard = this.add.image(320, 50, 'cardBack')
        .setDisplaySize(60, 90);
    remainingCard.value = lastCard.value;
    remainingCard.isFaceUp = false;
    remainingCard.backValue = backValue;
    flipCard(remainingCard);
}

let lastSelectedCard = null;
function selectCard(card) {
    if (card.clicked) return;

    // 直前に選択されたカードの透明度を元に戻す
    if (lastSelectedCard) {
        lastSelectedCard.setAlpha(0.5);
    }

    card.clicked = true;

    addPoint(card);
    updateDisplay();
    flipAdjacentCards(card.row, card.col);
    cardGrid[card.row][card.col] = null;

    // カードが表向きか裏向きかを確認し、適切な画像に変更
    if (card.isFaceUp) {
        card.setTexture(`card${card.value}_selected`);
    } else {
        card.setTexture('cardBack_selected');
    }
    card.disableInteractive(); // インタラクティブ機能を無効にする

    // カードを半透明にする
    //card.setAlpha(0.5);

    this.children.bringToTop(card);

    // 全てのカードのインタラクティブ機能を無効にする
    cardGrid.flat().forEach(c => {
        if (c) c.disableInteractive();
    });

    this.tweens.add({
        targets: card,
        scale: 0.3,
        duration: 190,
        yoyo: true,
        onComplete: () => {
            // アニメーション完了後に全てのカードのインタラクティブ機能を有効にする
            cardGrid.flat().forEach(c => {
                if (c && !c.clicked) c.setInteractive();
            });
        }
    });

    // 直前に選択されたカードとして保存
    lastSelectedCard = card;

    // カードを削除せずにそのまま配置
    this.time.delayedCall(500, () => {
        card.setPosition(card.x, card.y); // 位置を保持
    });
    this.time.delayedCall(500, () => {
        changePlayer();
        if (gameMode === "player_1") turnOfCpu = true;
        // ゲーム終了
        if (checkGameOver()) endGame.call(this);
        if (gameMode === "player_1" && turnOfCpu) {
            // プレイヤーが1人モードで、CPUのターンの場合
            cpuTurn.call(this);
        }
        updateDisplay(); // プレイヤーのターン変更後に表示を更新
    });
}


function cpuTurn() {
    if (checkGameOver()) return;

    // 直前に選択されたカードの透明度を元に戻す
    if (lastSelectedCard) {
        lastSelectedCard.setAlpha(0.5);
    }

    let card = cpuCard();

    // CPUのターンなので、currentPlayerをCPUに設定
    currentPlayer = playerNames[1] === "cpu" ? 1 : 2;

    addPoint(card);
    updateDisplay();
    flipAdjacentCards(card.row, card.col);
    cardGrid[card.row][card.col] = null;

    if (card.isFaceUp) {
        card.setTexture(`card${card.value}_selected`);
    } else {
        card.setTexture('cardBack_selected');
    }
    card.disableInteractive(); // インタラクティブ機能を無効にする

    // 直前に選択されたカードとして保存
    lastSelectedCard = card;

    this.children.bringToTop(card);

    // カードを拡大するアニメーション
    this.tweens.add({
        targets: card,
        scale: 0.3,
        duration: 190,
        yoyo: true
    });

    // カードを削除せずにそのまま配置
    this.time.delayedCall(500, () => {
        card.setPosition(card.x, card.y); // 位置を保持
    });

    changePlayer();
    turnOfCpu = false;

    if (checkGameOver()) {
        endGame.call(this);
    }
}



function cpuCard() {
    // CPUの手を決める
    let selectableCards = [];

    // 盤面の全カードを確認し、選択肢をリストにする
    for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
            let card = cardGrid[row][col];
            if (card !== null) { // 取れるカードだけをリストに追加
                if (card.isFaceUp) {
                    if (card.value === remainingCard.value) {
                        selectableCards.push({ score: card.value * -1, row: row, col: col });
                    } else {
                        selectableCards.push({ score: card.value, row: row, col: col });
                    }
                } else {
                    selectableCards.push({ score: card.backValue, row: row, col: col });
                }
            }
        }
    }

    // 得点が高い順にソート
    selectableCards.sort((a, b) => b.score - a.score);

    console.log(`ソートされたカード: ${JSON.stringify(selectableCards)}`);

    // 同じ得点のカードをリストに追加
    let highestScore = selectableCards[0].score;
    let highestScoreCards = selectableCards.filter(card => card.score === highestScore);

    // ランダムに選択
    let randomIndex = Phaser.Math.Between(0, highestScoreCards.length - 1);
    let bestCard = cardGrid[highestScoreCards[randomIndex].row][highestScoreCards[randomIndex].col];

    console.log(`CPUは (${highestScoreCards[randomIndex].row},${highestScoreCards[randomIndex].col}) を選択しました`);

    return bestCard;
}

function addPoint(card) {
    let points = card.isFaceUp ? card.value : card.backValue;
    if (card.isFaceUp && card.value === remainingCard.value) {
        points = -points;
    }
    playerScores[currentPlayer] += points;
}


function flipCard(card) {
    card.isFaceUp = !card.isFaceUp;
    card.setTexture(card.isFaceUp ? `card${card.value}` : 'cardBack');
}

function flipAdjacentCards(row, col) {
    const directions = [
        { dr: -1, dc: 0 }, { dr: 1, dc: 0 },
        { dr: 0, dc: -1 }, { dr: 0, dc: 1 }
    ];

    directions.forEach(({ dr, dc }) => {
        const adjacentRow = row + dr;
        const adjacentCol = col + dc;
        if (adjacentRow >= 0 && adjacentRow < 3 && adjacentCol >= 0 && adjacentCol < 3) {
            const adjacentCard = cardGrid[adjacentRow][adjacentCol];
            if (adjacentCard && !adjacentCard.clicked) { // 選択済みカードを裏返さない
                flipCard(adjacentCard);
            }
        }
    });
}

function changePlayer() {
    currentPlayer = currentPlayer === 1 ? 2 : 1;
}

function updateDisplay() {
    const clickablePlayer = gameMode === "player_1" && turnOfCpu ? playerNames[2] : playerNames[currentPlayer];
    currentPlayerText.setText(`プレイヤー: ${clickablePlayer}`)
        .setStyle({ padding: { top: 10, bottom: 10, left: 10, right: 10 } });
    scoreText.setText(`得点 ${playerNames[1]}: ${playerScores[1]} ${playerNames[2]}: ${playerScores[2]}`)
        .setStyle({ padding: { top: 10, bottom: 10, left: 10, right: 10 } });
}


function checkGameOver() {
    return cardGrid.every(row => row.every(card => card === null));
}

function endGame() {
    let winner;
    if (gameMode === "player_1") {
        console.log(playerNames);
        if (playerNames[1] === "you") {
            console.log("senko");
            winner = playerScores[1] > playerScores[2] ? 'You Win!' :
                playerScores[1] < playerScores[2] ? 'You Lose' : 'Draw';
        } else {
            winner = playerScores[1] < playerScores[2] ? 'You Win!' :
                playerScores[1] > playerScores[2] ? 'You Lose' : 'Draw';
        }
    } else {
        winner = playerScores[1] > playerScores[2] ? '1P' :
            playerScores[1] < playerScores[2] ? '2P' : '引き分け';
    }

    this.add.text(75, 150, `${winner}`, { fontSize: '24px', fill: '#fff', backgroundColor: '#444', padding: { top: 10, bottom: 10 } });
    senkou = false;
    manageCreate = true;
    createEndButtons.call(this);
}

let endButtons = [];

function createEndButtons() {
    console.log("aaaaa");
    const buttons = [
        { text: 'モード選択に戻る', y: 200, callback: () => resetGame.call(this, true) },
        { text: 'もう一度遊ぶ', y: 250, callback: resetGame.bind(this, false) } // false を渡して先行後攻選択画面から始める
    ];

    buttons.forEach(({ text, y, callback }) => {
        let button = this.add.text(75, y, text, { fontSize: '20px', fill: '#fff', backgroundColor: '#444', padding: { top: 10, bottom: 10 } })
            .setInteractive()
            .on('pointerdown', () => {
                callback();
                button.disableInteractive(); // インタラクティブ機能を無効にする
                button.destroy(); // ボタンを削除する
            });
        endButtons.push(button); // ボタンを配列に追加
    });
}

function resetGame(toModeSelection = false) {
    playerScores = { 1: 0, 2: 0 };
    currentPlayer = 1;
    cardGrid = Array.from({ length: 3 }, () => Array(3).fill(null));
    this.children.removeAll();

    // すべてのエンドボタンを削除
    endButtons.forEach(button => button.destroy());
    endButtons = [];

    scoreText = this.add.text(160, 310, `得点 P1: ${playerScores[1]} P2: ${playerScores[2]}`, { fontSize: '16px', fill: '#fff', padding: { top: 10, bottom: 10 } });
    currentPlayerText = this.add.text(10, 310, `プレイヤー: ${currentPlayer}`, { fontSize: '16px', fill: '#fff', padding: { top: 10, bottom: 10 } });

    if (toModeSelection) {
        createModeSelection.call(this);
    } else {
        createTurnSelection.call(this); // 先行後攻選択画面から始める
    }
}


function update() { }
