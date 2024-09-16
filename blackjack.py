import random, time
from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "OFHPdfhsupDFHIFB"

def startGame():
    session["player"] = [[random.randrange(1, 14), getRandomSuit()], [random.randrange(1, 14), getRandomSuit()]]
    session["dealer"] = [[random.randrange(1, 14), getRandomSuit()], "#"]
    session["playerAceCount"] = 0
    session["dealerAceCount"] = 0
    session["runningtotal"] = translateCardValue(session["player"][0][0]) + translateCardValue(session["player"][1][0])
    session["gameStatus"] = "In Progress"
    session["gameOver"] = False
    session["dealerRunningTotal"] = ""

    updatePlayerAceCount(session["player"][0][0])
    updatePlayerAceCount(session["player"][1][0])
    updateDealerAceCount(session["dealer"][0][0])
    updateDealerAceCount(session["dealer"][1][0])
    
    if session["playerAceCount"] == 2:
        session["runningtotal"] -= 10
        session["playerAceCount"] -= 1

def updatePlayerAceCount(card):
    if card == 1:
        session["playerAceCount"] += 1

def updateDealerAceCount(card):
    if card == 1:
        session["dealerAceCount"] += 1

def translateCardValue(card):
    if card == 11:
        return 10
    elif card == 12:
        return 10
    elif card == 13:
        return 10
    elif card == 1:
        return 11
    else:
        return card

def getRandomSuit():
    suit = random.randrange(1, 5)
    if suit == 1:
        return "hearts"
    if suit == 2:
        return "diams"
    if suit == 3:
        return "spades"
    if suit == 4:
        return "clubs"

def translateCardToRealName(cards):
    newSet = []
    for cardFull in cards:
        for cardNum in cardFull:
            if isinstance(cardNum, int) or cardNum == "#":
                if cardNum == 1:
                    newSet.append("rank-a " + cardFull[1])
                elif cardNum == 11:
                    newSet.append("rank-j " + cardFull[1])
                elif cardNum == 12:
                    newSet.append("rank-q " + cardFull[1])
                elif cardNum == 13:
                    newSet.append("rank-k " + cardFull[1])
                elif cardNum == "#":
                    newSet.append("back")
                else:
                    newSet.append("rank-" + str(cardNum) + " " + cardFull[1])
    return newSet

@app.route("/")
def index():
    if "player" not in session:
            startGame()
            if session["runningtotal"] == 21:
                return redirect(url_for("stand"))
    return render_template("index.html", player=translateCardToRealName(session["player"]), dealer=translateCardToRealName(session["dealer"]), runningtotal=session["runningtotal"], gameStatus=session["gameStatus"], dealerRunningTotal=session["dealerRunningTotal"]) 

@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return redirect(url_for("index"))

@app.route("/hit", methods=["POST"])
def hit():
    if session["gameOver"] != True:
        new_card = [random.randrange(1, 14), getRandomSuit()]
        session["player"].append(new_card)
        session["runningtotal"] += translateCardValue(new_card[0])
        updatePlayerAceCount(new_card[0])

        if session["playerAceCount"] >= 1 and session["runningtotal"] > 21:
            session["runningtotal"] -= 10
            session["playerAceCount"] -= 1

        if session["runningtotal"] > 21:
            session["gameStatus"] = "You Busted!"
            session["gameOver"] = True
            return redirect(url_for("index"))

        if session["runningtotal"] == 21:
            return redirect(url_for("stand"))
        
        return redirect(url_for("index"))
    return redirect(url_for("index"))

@app.route("/stand")
def stand():
    if session["gameOver"] != True:
        new_card = [random.randrange(1, 14), getRandomSuit()]
        session["dealer"].pop()
        session["dealer"].append(new_card)
        dealerRunningTotal = translateCardValue(session["dealer"][0][0]) + translateCardValue(session["dealer"][1][0])
        if session["dealerAceCount"] >= 1 and dealerRunningTotal > 21:
            dealerRunningTotal -= 10
            session["dealerAceCount"] -= 1
        while dealerRunningTotal < 21:
            if dealerRunningTotal < 17:
                new_card = [random.randrange(1, 14), getRandomSuit()]
                session["dealer"].append(new_card)
                dealerRunningTotal += translateCardValue(new_card[0])
                updateDealerAceCount(new_card[0])

                if session["dealerAceCount"] >= 1 and dealerRunningTotal > 21:
                    dealerRunningTotal -= 10
                    session["dealerAceCount"] -= 1
            else:
                break
        
        session["dealerRunningTotal"] = dealerRunningTotal

        if session["dealerRunningTotal"] > 21:
            session["gameStatus"] = "Dealer busts, You Win!"
            session["gameOver"] = True
        elif session["dealerRunningTotal"] > session["runningtotal"]:
            session["gameStatus"] = "Dealer higher, Dealer Wins!"
            session["gameOver"] = True
        elif session["dealerRunningTotal"] < session["runningtotal"]:
            session["gameOver"] = True
            session["gameStatus"] = "Player higher, Player Wins!"
        elif session["dealerRunningTotal"] == session["runningtotal"]:
            session["gameOver"] = True
            session["gameStatus"] = "Player and Dealer Tied!"

        return redirect(url_for("index", dealer=session["dealer"]))
    return redirect(url_for("index"))
if __name__ == "__main__":
    app.run(debug=True)