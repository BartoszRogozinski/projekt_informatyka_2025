#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <array>
#include <string> 
#include <fstream>
#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif
//MENU
class Menu {
private:
    sf::Font font;
    std::vector<std::string> opcje = { "GRAJ", "WCZYTAJ GRE", "INSTRUKCJE", "WYJSCIE" };
    int wybranaOpcja = 0;
    bool fontLoaded = false;

public:
    Menu() {
        if (!font.loadFromFile("arial.ttf")) {
            std::cout << "Nie mozna zaladowac czcionki arial.ttf\n";
        }
        else {
            fontLoaded = true;
        }
    }

    int run(sf::RenderWindow& window) {
        while (window.isOpen()) {
            sf::Event e;
            while (window.pollEvent(e)) {
                if (e.type == sf::Event::Closed)
                    window.close();

                if (e.type == sf::Event::KeyPressed) {
                    if (e.key.code == sf::Keyboard::A || e.key.code == sf::Keyboard::Left)
                        wybranaOpcja = (wybranaOpcja - 1 + opcje.size()) % opcje.size();

                    if (e.key.code == sf::Keyboard::D || e.key.code == sf::Keyboard::Right)
                        wybranaOpcja = (wybranaOpcja + 1) % opcje.size();

                    if (e.key.code == sf::Keyboard::Enter)
                        return wybranaOpcja;
                }
            }

            window.clear(sf::Color(20, 20, 20));

            for (size_t i = 0; i < opcje.size(); i++) {
                sf::Text text(opcje[i], font, 10);
                text.setPosition(100 + i * 150, 250);

                if (i == wybranaOpcja){
                    text.setFillColor(sf::Color::Yellow);
                    }
                else
                    text.setFillColor(sf::Color::White);

                window.draw(text);
            }

            window.display();
        }

        return 3; 
    }

    void instrukcje(sf::RenderWindow& window) {
        while (window.isOpen()) {
            sf::Event e;
            while (window.pollEvent(e)) {
                if (e.type == sf::Event::Closed)
                    window.close();
                if (e.type == sf::Event::KeyPressed && e.key.code == sf::Keyboard::Escape)
                    return;
            }

            window.clear(sf::Color(0, 0, 50));
            if (fontLoaded) {
                sf::Text t("Sterowanie:\nA/strzalka w lewo - w lewo\nD/strzalka w prawo - w prawo\nOdbij pilke i zbij klocki!\n\nF5 - zapisz gre\n\nESC - powrot",
                    font, 30);
                t.setPosition(150, 150);
                t.setFillColor(sf::Color::White);
                window.draw(t);
            }
            window.display();
        }
    }
};
//BLOKI
class Stone : public sf::RectangleShape {
private:
    int m_hp;
    bool m_destroyed;
    static const std::array<sf::Color, 4> LUT;

public:
    int getHP() const { return m_hp; }
    Stone(sf::Vector2f pos, sf::Vector2f size, int L)
        : m_hp(L), m_destroyed(false)
    {
        setPosition(pos);
        setSize(size);
        setOutlineThickness(2);
        setOutlineColor(sf::Color::Black);
        updateColor();
    }

    void hit() {
        if (m_destroyed) return;
        m_hp--;
        updateColor();
        if (m_hp <= 0) m_destroyed = true;
    }

    void updateColor() {
        setFillColor(LUT[m_hp]);
    }

    bool dead() const { return m_destroyed; }

    void draw(sf::RenderTarget& t) const {
        if (!m_destroyed)
            t.draw(*this);
    }

    sf::Vector2f getPos() const { return getPosition(); }
};

const std::array<sf::Color, 4> Stone::LUT = {
    sf::Color::Transparent,
    sf::Color::Red,
    sf::Color::Yellow,
    sf::Color::Blue
};
//PALETKA
class Paletka {
private:
    sf::RectangleShape shape;
    sf::Vector2f vel{ 400.f, 0.f };

public:
    Paletka(sf::Vector2f pos, sf::Vector2f size, sf::Vector2f v) {
        vel = v;
        shape.setPosition(pos);
        shape.setSize(size);
        shape.setFillColor(sf::Color::White);
    }

    void ruch(sf::Time dt) {
        if (sf::Keyboard::isKeyPressed(sf::Keyboard::A) || sf::Keyboard::isKeyPressed(sf::Keyboard::Left))
            shape.move({ -vel.x * dt.asSeconds(), 0 });
        if (sf::Keyboard::isKeyPressed(sf::Keyboard::D) || sf::Keyboard::isKeyPressed(sf::Keyboard::Right))
            shape.move({ vel.x * dt.asSeconds(), 0 });
    }

    void draw(sf::RenderTarget& w) { w.draw(shape); }
    sf::FloatRect getGlobalBounds() const { return shape.getGlobalBounds(); }

    sf::Vector2f getPosition() const { return shape.getPosition(); }
    void setPosition(const sf::Vector2f& pos) { shape.setPosition(pos); }
};

//PI£KA
class Pilka {
private:
    sf::CircleShape shape;
    sf::Vector2f vel{ 200.f, 200.f };

public:
    sf::Vector2f getVelocity() const { return vel; }
    sf::Vector2f getPosition() const { return shape.getPosition(); }

    Pilka(sf::Vector2f pos, float r, sf::Vector2f v) {
        vel = v;
        shape.setRadius(r);
        shape.setOrigin(r, r);
        shape.setPosition(pos);
        shape.setFillColor(sf::Color::Green);
    }

    void ruch(sf::Time dt, sf::Vector2f wh) {
        shape.move(vel * dt.asSeconds());
        float x = shape.getPosition().x;
        float y = shape.getPosition().y;
        float r = shape.getRadius();

        if (x - r <= 0 || x + r >= wh.x)
            vel.x = -vel.x;

        if (y - r <= 0)
            vel.y = -vel.y;
    }

    void zpredkosci(float mnoznik) {
        vel.x *= mnoznik;
        vel.y *= mnoznik;
    }

    float getRadius() const { return shape.getRadius(); }

    void setY(float y) {
        auto p = shape.getPosition();
        p.y = y;
        shape.setPosition(p);
    }

    void odbicieY() { vel.y = -vel.y; }
    void draw(sf::RenderTarget& w) { w.draw(shape); }
    sf::FloatRect getGlobalBounds() const { return shape.getGlobalBounds(); }

    void setPosition(const sf::Vector2f& pos) { shape.setPosition(pos); }
    void setVelocity(const sf::Vector2f& v) { vel = v; }
};
struct BlockData {
    float x, y;
    int hp;
};

//KLASA STANU GRY
class GameState {
private:
    sf::Vector2f paddlePosition;
    sf::Vector2f ballPosition;
    sf::Vector2f ballVelocity;
    std::vector<BlockData> blocks;
    int score = 0;

public:
    GameState() = default;

    void capture(const Paletka& p, const Pilka& b, const std::vector<Stone>& stones, int currentScore) {
        paddlePosition = p.getPosition();
        ballPosition = b.getPosition();
        ballVelocity = b.getVelocity();
        score = currentScore;

        blocks.clear();
        blocks.reserve(stones.size());

        for (const auto& s : stones) {
            if (!s.dead()) {
                BlockData bd;
                bd.x = s.getPos().x;
                bd.y = s.getPos().y;
                bd.hp = s.getHP();
                blocks.push_back(bd);
            }
        }
    }

    bool saveToFile(const std::string& filename) {
        std::ofstream file(filename);
        if (!file.is_open()) return false;

        file << "PADDLE " << paddlePosition.x << " " << paddlePosition.y << "\n";
        file << "BALL " << ballPosition.x << " " << ballPosition.y << " "
            << ballVelocity.x << " " << ballVelocity.y << "\n";
        file << "SCORE " << score << "\n";
        file << "BLOCKS_COUNT " << blocks.size() << "\n";
        for (const auto& block : blocks) {
            file << block.x << " " << block.y << " " << block.hp << "\n";
        }

        file.close();
        return true;
    }

    bool loadFromFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) return false;

        std::string label;

        if (!(file >> label >> paddlePosition.x >> paddlePosition.y)) return false;

        if (!(file >> label >> ballPosition.x >> ballPosition.y >> ballVelocity.x >> ballVelocity.y)) return false;

        if (!(file >> label >> score)) return false;

        int blocksCount;
        if (!(file >> label >> blocksCount)) return false;

        blocks.clear();
        blocks.reserve(blocksCount);
        for (int i = 0; i < blocksCount; ++i) {
            BlockData bd;
            if (!(file >> bd.x >> bd.y >> bd.hp)) return false;
            blocks.push_back(bd);
        }

        file.close();
        return true;
    }

    void apply(Paletka& p, Pilka& b, std::vector<Stone>& stones, int& currentScore, const sf::Vector2f& blockSize) {

        p.setPosition(paddlePosition);


        b.setPosition(ballPosition);
        b.setVelocity(ballVelocity);

        currentScore = score;

        stones.clear();
        for (const auto& data : blocks) {
            stones.emplace_back(sf::Vector2f(data.x, data.y), blockSize, data.hp);
        }
    }

    const sf::Vector2f& getPaddlePos() const { return paddlePosition; }
    const sf::Vector2f& getBallPos() const { return ballPosition; }
    const sf::Vector2f& getBallVel() const { return ballVelocity; }
    const std::vector<BlockData>& getBlocks() const { return blocks; }
    int getScore() const { return score; }
};
//GRA
class Game {
private:
    sf::RenderWindow window;
    sf::Clock clock;
    sf::Font font;
    sf::Text scoreText;

    int score = 0;
    sf::Vector2f blockSize; 

    Paletka paletka;
    Pilka pilka;
    std::vector<Stone> bloki;

    void updateScoreDisplay() {
        scoreText.setString("Punkty: " + std::to_string(score));
    }

public:
    Game()
        : window(sf::VideoMode(800, 600), "Arkanoid"),
        paletka({ 350,550 }, { 100,20 }, { 600,0 }),
        pilka({ 400,300 }, 15, { 250,250 })
    {
        window.setFramerateLimit(60);

        if (!font.loadFromFile("arial.ttf")) {
            std::cout << "Nie mozna zaladowac czcionki dla punktow\n";
        }


        scoreText.setFont(font);
        scoreText.setCharacterSize(20);
        scoreText.setFillColor(sf::Color::White);
        scoreText.setPosition(10, 10);

        const int COL = 6, ROW = 7;
        const float gap = 2.f;
        const float H = 25, W = (800 - (COL - 1) * gap) / COL;
        blockSize = sf::Vector2f(W, H); 

        for (int y = 0; y < ROW; y++)
            for (int x = 0; x < COL; x++) {
                int hp = (y < 1) ? 3 : (y < 3) ? 2 : 1;
                bloki.emplace_back(
                    sf::Vector2f(x * (W + gap), 50 + y * (H + gap)),
                    sf::Vector2f(W, H),
                    hp
                );
            }

        updateScoreDisplay();
    }

    Game(bool loadFromSave) : Game() {
        if (loadFromSave) {
            GameState gs;
            if (gs.loadFromFile("savegame.txt")) {
                gs.apply(paletka, pilka, bloki, score, blockSize);
                updateScoreDisplay();
            }
        }
    }

    bool run() {
        while (window.isOpen()) {
            sf::Time dt = clock.restart();
            process();
            update(dt);
            render();

            if (pilka.getGlobalBounds().top > 600)
                return false;
        }
        return false;
    }

    void process() {
        sf::Event e;
        while (window.pollEvent(e)) {
            if (e.type == sf::Event::Closed)
                window.close();
            if (e.type == sf::Event::KeyPressed && e.key.code == sf::Keyboard::F5) {
                GameState gs;
                gs.capture(paletka, pilka, bloki, score);
                if (gs.saveToFile("savegame.txt")) {
                    std::cout << "Gra zapisana!\n";
                }
            }
        }
    }

    void update(sf::Time dt) {
        paletka.ruch(dt);
        pilka.ruch(dt, { 800,600 });

        if (pilka.getGlobalBounds().intersects(paletka.getGlobalBounds()))
        {
            pilka.odbicieY();

            float paddleTop = paletka.getGlobalBounds().top;
            pilka.setY(paddleTop - pilka.getRadius() - 1);
        }

        for (auto& b : bloki) {
            if (!b.dead() && pilka.getGlobalBounds().intersects(b.getGlobalBounds())) {
                int points = 0;
                if (b.getHP() == 3) points = 30;
                else if (b.getHP() == 2) points = 20;
                else if (b.getHP() == 1) points = 10;

                score += points;
                updateScoreDisplay();

                b.hit();
                pilka.odbicieY();
                pilka.zpredkosci(1.015f);
            }
        }
    }

    void render() {
        window.clear(sf::Color::Blue);
        paletka.draw(window);
        pilka.draw(window);

        for (auto& b : bloki)
            b.draw(window);
        window.draw(scoreText);

        window.display();
    }

    sf::RenderWindow& getWindow() { return window; }

    int getScore() const { return score; }
};

//MAIN
int main() {
    Game* g = new Game();
    Menu menu;

    while (true) {
        int opcja = menu.run(g->getWindow());

        if (opcja == 0) { 
            delete g;
            g = new Game();
            g->run();
        }
        else if (opcja == 1) { 
            delete g;
            g = new Game(true); 
            g->run();
        }
        else if (opcja == 2) { 
            menu.instrukcje(g->getWindow());
        }
        else if (opcja == 3) { 
            delete g;
            return 0;
        }
    }
}