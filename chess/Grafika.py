import pygame as p
from chess import Logika

SIRINA = VISINA = 512
DIMENZIJA = 8
SQ_SIZE = VISINA // DIMENZIJA
MAX_FPS = 15
SLIKE = {}


def ucitajSlike():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        SLIKE[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((SIRINA, VISINA))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Logika.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    ucitajSlike()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = Logika.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                print(gs.whiteToMove)
                                gs.makeMove(validMoves[i])
                                print(gs.whiteToMove)
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_y:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_u:

                    gs.getBestMove()


                    gs.makeMove(gs.bestMove)
                    moveMade = True
                    animate = True
                    sqSelected = ()
                    playerClicks = []
                if e.key == p.K_r:
                    gs = Logika.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animirajPotez(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        stanjeNaPloci(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                ispisiText(screen, 'Pobjeda crnog sahmatom')
            else:
                ispisiText(screen, 'Pobjeda bijelog sahmatom')
        elif gs.stalemate:
            gameOver = True
            ispisiText(screen, 'Pat')
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Oznacava odabranu figuru i polja na koja se moze pomaknuti
'''
def oznaciPolja(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #oznaciti odabrano polje
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency vrijednost 0 prozirno 255 neprozirno
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #oznaciti polja na koja mozemo pomaknuti figuru
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol ==c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


def stanjeNaPloci(screen, gs, validMoves, sqSelected):
    nacrtajPlocu(screen)
    oznaciPolja(screen, gs, validMoves, sqSelected)
    nacrtajFigure(screen, gs.board)

def nacrtajPlocu(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENZIJA):
        for c in range(DIMENZIJA):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r* SQ_SIZE, SQ_SIZE, SQ_SIZE))


def nacrtajFigure(screen, board):
    for r in range(DIMENZIJA):
        for c in range(DIMENZIJA):
            piece = board[r][c]
            if piece != "--":
                screen.blit(SLIKE[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animiranje poteza
'''
def animirajPotez(move, screen, board, clock):
    global colors
    coords = []
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/(frameCount+1), move.startCol + dC*frame/(frameCount+1))
        nacrtajPlocu(screen)
        nacrtajFigure(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(SLIKE[move.pieceCaptured], endSquare)
        screen.blit(SLIKE[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def ispisiText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, SIRINA, VISINA).move(SIRINA / 2 - textObject.get_width() / 2, VISINA / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()
