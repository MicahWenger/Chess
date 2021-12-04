
import Chess

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.config import Config

from kivy.clock import Clock


class ChessApp(App):
    def build(self):
        gameScreen = Chess.GameScreen(self.chessConfig)
        gameScreen.players = [Chess.Player('USER', 0),Chess.Player('MW_AI', 1)]
        # Clock.schedule_interval(gameScreen.nextMove, 0.1)
        return gameScreen

def main():
    app = ChessApp()
    app.chessConfig = Chess.ChessConfig(8,8, 800,800)
    Window.size = (app.chessConfig.dimX, app.chessConfig.dimY)
    app.run()

if __name__ == '__main__':
    main()
