
import sys, pygame
import time, random
import threading

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700

BACKGROUND_COLOR = (46, 52, 64)

SCORE_BOARD_TEXT_COLOR = (255, 255, 255)
SCORE_BOARD_FONT_SIZE = 48

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 120
PADDLE_Y_MOVE_AMOUNT = 7

PADDLE_COLOR = (255, 255, 255)
BALL_FILL_COLOR = (255, 255, 255)
BALL_BORDER_COLOR = (0, 0, 0)

BALL_PLAYER_SERVE_XRANGE = -4, -4
BALL_PLAYER_SERVE_YRANGE = -4, 4
BALL_OPPONENT_SERVE_XRANGE = 3, 5
BALL_OPPONENT_SERVE_YRANGE = -4, 4

BALL_BOUNCE_REDUCTION_FACTOR = 8

BALL_RADIUS = 4

FIELD_COLOR = (255, 255, 255)
FIELD_CIRCLE_WIDTH = 1
FIELD_CIRCLE_RADIUS = 100

FIELD_GOAL_XOFFSET = 40

AI_SENSITIVITY = 40

OPPONENT_SERVE_DELAY = 2000

FPS = 60
fpsClock = pygame.time.Clock()

class Utils:

    @staticmethod
    def getMiddlePosition():
        return [int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2)]

    @staticmethod
    def getMiddleXPosition():
        return int(SCREEN_WIDTH / 2)

    @staticmethod
    def getMiddleYPosition():
        return int(SCREEN_HEIGHT / 2)

    @staticmethod
    def getRandomDirection():
        directions = ['right', 'left', 'down', 'up']
        initialDirection = directions[random.randint(0, 3)]
        return initialDirection

    @staticmethod
    def sign(n):
        if n<0:
            return -1
        elif n>0:
            return 1
        else: 0

class Sound:


    @staticmethod
    def init():
        Sound.SND_BALL_HIT_WALL = pygame.mixer.Sound("ballhitwall.wav")
        Sound.SND_BALL_HIT_PADDLE = pygame.mixer.Sound("ballhitpaddle.wav")

        Sound.SND_GAME_OVER = pygame.mixer.Sound("gameover.wav")
        Sound.SND_GAME_MUSIC = pygame.mixer.Sound("gamemusic.wav")

    @staticmethod
    def playBallHitWallSound():
        pygame.mixer.Sound.play(Sound.SND_BALL_HIT_WALL)
        pygame.mixer.music.stop()

    @staticmethod
    def playBallHitPaddleSound():
        pygame.mixer.Sound.play(Sound.SND_BALL_HIT_PADDLE)
        pygame.mixer.music.stop()

    @staticmethod
    def playGameOver():
        pygame.mixer.Sound.play(Sound.SND_GAME_OVER)
        pygame.mixer.Sound.set_volume(Sound.SND_GAME_OVER, 0.4)
        pygame.mixer.music.stop()


class Scoreboard:

    @staticmethod
    def init():

        Scoreboard.playerScore = 0
        Scoreboard.opponentScore = 0

        Scoreboard.setPlayerScore(Scoreboard.playerScore)
        Scoreboard.setOpponentScore(Scoreboard.opponentScore)

    @staticmethod
    def setOpponentScore(score):
        Scoreboard.opponentScore = score
        Scoreboard.opponentScoreText = str(score)

    @staticmethod
    def addToOpponentScore():
        Scoreboard.opponentScore += 1
        Scoreboard.opponentScoreText = str(Scoreboard.opponentScore)

    @staticmethod
    def setPlayerScore(score):
        Scoreboard.playerScore = score
        Scoreboard.playerScoreText = str(score)

    @staticmethod
    def addToPlayerScore():
        Scoreboard.playerScore += 1
        Scoreboard.playerScoreText = str(Scoreboard.playerScore)



class Renderer:

    @staticmethod
    def __drawBackground():
        screen.fill(BACKGROUND_COLOR)

    @staticmethod
    def __drawField():
        pygame.draw.line(screen, FIELD_COLOR, (Utils.getMiddleXPosition(), 0), (Utils.getMiddleXPosition(), SCREEN_HEIGHT))
        pygame.draw.circle(screen, FIELD_COLOR, Utils.getMiddlePosition(), FIELD_CIRCLE_RADIUS, FIELD_CIRCLE_WIDTH)

    @staticmethod
    def __drawScoreboard():
        font = pygame.font.SysFont(None, SCORE_BOARD_FONT_SIZE)
        img = font.render(Scoreboard.playerScoreText, True, SCORE_BOARD_TEXT_COLOR)
        screen.blit(img, (SCREEN_WIDTH / 2 - 100, 25))
        img = font.render(Scoreboard.opponentScoreText, True, SCORE_BOARD_TEXT_COLOR)
        screen.blit(img, (SCREEN_WIDTH / 2 + 85, 25))

    @staticmethod
    def __drawPaddle(paddle):
        paddleRect = pygame.Rect((paddle.position[0],
                                paddle.position[1],
                                paddle.width, paddle.height))
        pygame.draw.rect(screen, PADDLE_COLOR, paddleRect)

    @staticmethod
    def __drawBall():
        ball = Ball.ball
        pygame.draw.circle(screen, BALL_FILL_COLOR,
                           ball.position, ball.radius, 0)

    @staticmethod
    def draw():

        Renderer.__drawBackground()
        Renderer.__drawField()
        Renderer.__drawPaddle(Paddle.userPaddle)
        Renderer.__drawPaddle(Paddle.aiPaddle)
        Renderer.__drawBall()
        Renderer.__drawScoreboard()

class Ball:

    def __init__(self, pos, movement=[0,0], radius=BALL_RADIUS):
        self.position = pos
        self.radius = radius
        self.movementFactor = 1
        self.originalMovement = [movement[0],movement[1]]
        self.movement = [movement[0],movement[1]]
        self.released = False
        self.serve = 'player'

    def update(self):

        if not self.released:
            return None

        self.position[0] += self.movement[0]
        self.position[1] += self.movement[1]

class Paddle:

    def __init__(self, pos):
        self.position = pos
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.direction = 'none'

    def update(self):
        if self.direction == 'up':
            self.position[1] += -PADDLE_Y_MOVE_AMOUNT
        elif self.direction == 'down':
            self.position[1] += PADDLE_Y_MOVE_AMOUNT


class GameWorld:

    @staticmethod
    def init():

        Sound.init()
        Scoreboard.init()

        Ball.ball = Ball(Utils.getMiddlePosition(), [random.randint(BALL_PLAYER_SERVE_XRANGE[0], BALL_PLAYER_SERVE_XRANGE[1]),
                                                     random.randint(BALL_PLAYER_SERVE_YRANGE[0], BALL_PLAYER_SERVE_YRANGE[1])])
        Paddle.userPaddle = Paddle([PADDLE_WIDTH, Utils.getMiddleYPosition()-PADDLE_HEIGHT/2])
        Paddle.aiPaddle = Paddle([SCREEN_WIDTH-PADDLE_WIDTH*2, Utils.getMiddleYPosition() - PADDLE_HEIGHT / 2])



    @staticmethod
    def reset():

        Scoreboard.init()

        del Paddle.userPaddle
        del Paddle.aiPaddle
        del Ball.ball

        Ball.ball = Ball(Utils.getMiddlePosition(), [random.randint(BALL_PLAYER_SERVE_XRANGE[0], BALL_PLAYER_SERVE_XRANGE[1]),
                                                     random.randint(BALL_PLAYER_SERVE_YRANGE[0][0], BALL_PLAYER_SERVE_YRANGE[1])])
        Paddle.userPaddle = Paddle([PADDLE_WIDTH, Utils.getMiddleYPosition()-PADDLE_HEIGHT/2])
        Paddle.aiPaddle = Paddle([SCREEN_WIDTH-PADDLE_WIDTH*2, Utils.getMiddleYPosition() - PADDLE_HEIGHT / 2])

    @staticmethod
    def __resetField():

        ball.released = False
        ball.position = Utils.getMiddlePosition()

        if ball.serve == 'player':
            ball.movement = [random.randint(BALL_PLAYER_SERVE_XRANGE[0], BALL_PLAYER_SERVE_XRANGE[1]),
                             random.randint(BALL_PLAYER_SERVE_YRANGE[0], BALL_PLAYER_SERVE_YRANGE[1])]
        elif ball.serve == 'opponent':
            ball.movement = [random.randint(BALL_OPPONENT_SERVE_XRANGE[0], BALL_OPPONENT_SERVE_XRANGE[1]),
                             random.randint(BALL_OPPONENT_SERVE_YRANGE[0], BALL_OPPONENT_SERVE_YRANGE[1])]

        Paddle.userPaddle = Paddle([PADDLE_WIDTH, Utils.getMiddleYPosition()-PADDLE_HEIGHT/2])
        Paddle.aiPaddle = Paddle([SCREEN_WIDTH-PADDLE_WIDTH*2, Utils.getMiddleYPosition() - PADDLE_HEIGHT / 2])

    @staticmethod
    def quit():
        return None

    @staticmethod
    def __update_PaddleBoundaries(paddle):
        if paddle.position[1] <= 0:
            paddle.position[1] = 0
        elif paddle.position[1] + paddle.height >= SCREEN_HEIGHT:
            paddle.position[1] = SCREEN_HEIGHT - paddle.height

    @staticmethod
    def __update_AIPaddle():
        aiPaddle = Paddle.aiPaddle
        ball = Ball.ball

        if ball.position[1] + ball.radius < (aiPaddle.position[1] + aiPaddle.height / 2) - AI_SENSITIVITY:
            aiPaddle.direction = 'up'
        elif ball.position[1] + ball.radius > (aiPaddle.position[1] + aiPaddle.height / 2) + AI_SENSITIVITY:
            aiPaddle.direction = 'down'
        else:
            aiPaddle.direction = 'none'

    @staticmethod
    def __update_BallBoundaries():
        ball = Ball.ball
        if ball.position[0]+ball.radius <= -FIELD_GOAL_XOFFSET:
            Scoreboard.addToOpponentScore()
            ball.serve = 'player'
            GameWorld.__resetField()
            return None
        elif ball.position[0] >= SCREEN_WIDTH + FIELD_GOAL_XOFFSET:
            Scoreboard.addToPlayerScore()
            ball.serve = 'opponent'
            GameWorld.__resetField()
            return None
        elif ball.position[1]-ball.radius <= 0:
            ball.position[1] = ball.radius+1
            ball.movement[1] *= -1
            Sound.playBallHitWallSound()
        elif ball.position[1] + ball.radius >= SCREEN_HEIGHT:
            ball.movement[1] *= -1
            ball.position[1] = SCREEN_HEIGHT - ball.radius - 1
            Sound.playBallHitWallSound()

    @staticmethod
    def update():

        userPaddle = Paddle.userPaddle
        aiPaddle = Paddle.aiPaddle
        ball = Ball.ball

        aiPaddle.update()
        userPaddle.update()
        ball.update()

        GameWorld.__update_PaddleBoundaries(Paddle.userPaddle)
        GameWorld.__update_PaddleBoundaries(Paddle.aiPaddle)

        GameWorld.__update_BallBoundaries()

        GameWorld.__update_AIPaddle()

        if ball.position[1]+ball.radius>=userPaddle.position[1] and \
                ball.position[0]+ball.radius >= userPaddle.position[0] and \
                ball.position[0]-ball.radius <= userPaddle.position[0]+userPaddle.width and \
                ball.position[1]+ball.radius<=userPaddle.position[1]+userPaddle.height:

            Sound.playBallHitPaddleSound()

            if ball.position[1] < userPaddle.position[1]+userPaddle.height/2:
                maxval = abs(ball.position[1] - (userPaddle.position[1] + userPaddle.height / 2)) / BALL_BOUNCE_REDUCTION_FACTOR
                ball.movement[1] = -maxval * ball.movementFactor
            elif ball.position[1] >= userPaddle.position[1]+userPaddle.height/2:
                maxval = abs(((userPaddle.position[1] + userPaddle.height / 2) - ball.position[1])) / BALL_BOUNCE_REDUCTION_FACTOR
                ball.movement[1] = maxval * ball.movementFactor

            ball.movement[0] *= -1
            ball.position[0] = userPaddle.position[0]+userPaddle.width + ball.radius + 1

        if ball.position[1]+ball.radius>=aiPaddle.position[1] and \
                ball.position[0]+ball.radius >= aiPaddle.position[0] and \
                ball.position[0]-ball.radius <= aiPaddle.position[0]+aiPaddle.width and \
                ball.position[1]+ball.radius<=aiPaddle.position[1]+aiPaddle.height:

            Sound.playBallHitPaddleSound()

            if ball.position[1] < aiPaddle.position[1]+aiPaddle.height/2:
                maxval = abs(ball.position[1] - (aiPaddle.position[1] + aiPaddle.height / 2)) / BALL_BOUNCE_REDUCTION_FACTOR
                ball.movement[1] = -maxval * ball.movementFactor
            elif ball.position[1] >= aiPaddle.position[1]+aiPaddle.height/2:
                maxval = abs(((aiPaddle.position[1] + aiPaddle.height / 2) - ball.position[1])) / BALL_BOUNCE_REDUCTION_FACTOR
                ball.movement[1] = maxval * ball.movementFactor

            ball.movement[0] *= -1
            ball.position[0] = aiPaddle.position[0] - ball.radius - 1

if __name__ == '__main__':

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Pong")

    prev_time = time.time()

    GameWorld.init()

    running = True
    bOpponentServeTimerSet = False
    opponent_serve = None

    while running:

        userPaddle = Paddle.userPaddle
        ball = Ball.ball

        if ball.serve == 'opponent' and not bOpponentServeTimerSet:
            opponent_serve = pygame.USEREVENT + 1
            pygame.time.set_timer(opponent_serve, OPPONENT_SERVE_DELAY, 1)
            bOpponentServeTimerSet = True


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == opponent_serve:
                ball.serve = 'none'
                ball.released = True
                bOpponentServeTimerSet = False


        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and ball.serve == 'player':
            ball.released = True

        if keys[pygame.K_UP] and userPaddle.direction is not 'down':
            userPaddle.direction = 'up'
        elif keys[pygame.K_DOWN] and userPaddle.direction is not 'up':
            userPaddle.direction = 'down'
        else:
            userPaddle.direction = 'none'

        GameWorld.update()

        Renderer.draw()

        pygame.display.flip()
        fpsClock.tick(FPS)

    GameWorld.quit()
