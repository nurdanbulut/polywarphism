import tkinter as tk
from tkinter import simpledialog, messagebox

class Warrior:
    def __init__(self, name, attack, health, attack_range, cost, player_id):
        self.name = name
        self.attack = attack
        self.health = health
        self.attack_range = attack_range
        self.cost = cost
        self.x = 0
        self.y = 0
        self.player_id = player_id

    
    def find_targets_in_range(self, all_warriors, horizontal_range, vertical_range, diagonal_range, friendly=False):
        targets = []
        for dx in range(-max(horizontal_range, diagonal_range), max(horizontal_range, diagonal_range) + 1):
            for dy in range(-max(vertical_range, diagonal_range), max(vertical_range, diagonal_range) + 1):
                # Kendi konumunu atla
                if dx == 0 and dy == 0:
                    continue
                # Dikey menzil dışında kalıyorsa atla
                if abs(dy) > vertical_range:
                    continue
                # Yatay menzil dışında kalıyorsa atla
                if abs(dx) > horizontal_range:
                    continue
                # Çapraz menzil için kontrol et ve uygun değilse atla
                if diagonal_range == 0 and abs(dx) == abs(dy):
                    continue
                # Çapraz menzil dışında kalıyorsa atla
                if diagonal_range > 0 and abs(dx) != abs(dy):
                    continue

                x, y = self.x + dx, self.y + dy
                # Menzil dışına çıkmayı kontrol et
                if not (0 <= x < self.world_size and 0 <= y < self.world_size):
                    continue

                for warrior in all_warriors:
                    if warrior.x == x and warrior.y == y and ((friendly and warrior.player_id == self.player_id) or
                                                               (not friendly and warrior.player_id != self.player_id)):
                        targets.append(warrior)
        return targets

    def perform_action(self, all_warriors,world_size):
        # Bu metod alt sınıflarda özelleştirilecek
        pass
class Guardian(Warrior):
    def __init__(self, player_id):
        super().__init__("Muhafız", 10, 80, 1, 0, player_id)
        self.max_health = 80

    def perform_action(self, all_warriors,world_size):
        # Menzildeki tüm düşmanlara saldır
        self.world_size = world_size
        targets = self.find_targets_in_range(all_warriors, 1,1,1)
        for target in targets:
            target.health -= 20

class Archer(Warrior):
    def __init__(self, player_id):
        super().__init__("Okçu", 20, 30, 2, 20, player_id)
        self.max_health = 30

    def perform_action(self, all_warriors,world_size):
        # Menzildeki en yüksek cana sahip 3 düşmana saldır
        self.world_size = world_size
        targets = self.find_targets_in_range(all_warriors, 2,2,2)
        targets.sort(key=lambda w: -w.health)
        for target in targets[:3]:
            target.health -= int(target.health * 0.6)

class Cannon(Warrior):
    def __init__(self, player_id):
        super().__init__("Topçu", 50, 30, 2, 50, player_id)
        self.max_health = 30

    def perform_action(self, all_warriors,world_size):
        # Menzildeki en yüksek cana sahip 1 düşmana saldır
        self.world_size = world_size
        targets = self.find_targets_in_range(all_warriors, self.attack_range, self.attack_range, diagonal_range=0)
        if targets:
            highest_health_target = max(targets, key=lambda w: w.health)
            highest_health_target.health -= int(highest_health_target.health * 1) 

class Cavalry(Warrior):
    def __init__(self, player_id):
        super().__init__("Atlı", 30, 40, 3, 30, player_id)
        self.max_health = 40

    def perform_action(self, all_warriors,world_size):
        # Menzildeki en pahalı 2 düşmana çapraz saldır
        self.world_size = world_size
        targets = self.find_targets_in_range(all_warriors, 0,0,diagonal_range=self.attack_range)
        targets.sort(key=lambda w: -w.cost)
        for target in targets[:2]:
            target.health -= 30

class Medic(Warrior):
    def __init__(self, player_id):
        super().__init__("Sağlıkçı", 10, 100, 2, 10, player_id)
        self.max_health = 100

    def perform_action(self, all_warriors,world_size):
        self.world_size = world_size
        # Menzildeki en az cana sahip olan 3 dost birliği iyileştir
        targets = self.find_targets_in_range(all_warriors, 2,2,2, friendly=True)
        targets.sort(key=lambda w: w.health)
        for target in targets[:3]:
            target.health += int(target.max_health * 0.5)
            target.health = min(target.health, target.max_health)
class Player:
    def __init__(self, player_id, health=100, resources=200):
        self.player_id = player_id
        self.health = health
        self.resources = resources
        self.warriors = []
        self.passed_turns = 0
        self.eliminated = False
        
        

    def create_warrior(self, warrior_type, x, y, game_board):
        if warrior_type == "Guardian":
            warrior = Guardian(self.player_id)
        elif warrior_type == "Archer":
            warrior = Archer(self.player_id)
        elif warrior_type == "Cannon":
            warrior = Cannon(self.player_id)
        elif warrior_type == "Cavalry":
            warrior = Cavalry(self.player_id)
        elif warrior_type == "Medic":
            warrior = Medic(self.player_id)
        else:
            return False  # Geçersiz savaşçı tipi

        # Yeterli kaynak var mı kontrol et ve savaşçıyı yerleştir
        if self.resources >= warrior.cost:
            placed = game_board.place_warrior(x, y, warrior)
            if placed:
                self.resources -= warrior.cost
                warrior.x = x
                warrior.y = y
                self.warriors.append(warrior)
                return True
        return False
    
    def add_warrior(self, warrior_type):
        # Yeni savaşçı ekleme
        if self.resources >= warrior_type.cost:
            self.warriors.append(warrior_type)
            self.resources -= warrior_type.cost
            print(f"{warrior_type.name} added to Player {self.player_id}'s army. Remaining resources: {self.resources}")
        else:
            print("Not enough resources to add this warrior.")

    def display_warriors(self):
        # Oyuncunun savaşçılarını gösterme
        if self.warriors:
            print(f"Player {self.player_id}'s warriors:")
            for warrior in self.warriors:
                print(f"- {warrior.name} (Health: {warrior.health}, Attack: {warrior.attack})")
        else:
            print(f"Player {self.player_id} has no warriors.")

    def attack_with_warrior(self, warrior_index, target_player):
        # Belirli bir savaşçı ile saldırı yapma
        if 0 <= warrior_index < len(self.warriors):
            warrior = self.warriors[warrior_index]
            # Basit bir saldırı mekanizması örneği
            # Burada daha karmaşık etkileşimler tanımlanabilir
            print(f"Player {self.player_id}'s {warrior.name} attacks Player {target_player.player_id}!")
            # Saldırı sonuçlarını işle, örneğin hedef oyuncunun canını azalt
        else:
            print("Invalid warrior index.")
class GameGUI:
    def __init__(self, master):
        self.world_size = self.ask_world_size()
        self.player_count = self.ask_player_count()
        self.master = master
        self.master.deiconify()
        self.master.title("Lords of the Polywarphism")
        self.players = [Player(player_id) for player_id in range(1, self.player_count + 1)]  # Oyuncuları saklamak için bir liste oluşturuluyor
        self.cells = {}  # (row, col): button
        self.init_gui()
        self.turn_label = tk.Label(self.master, text="", font=("Helvetica", 16))
        self.turn_label.pack()
        self.pass_button = tk.Button(self.master, text="Pass Turn", command=self.pass_turn)
        self.pass_button.pack()
        self.current_player_index = 0  # İlk oyuncuyla başla
        self.current_player_actions = 0 
        self.warrior_info_panels = {}
        self.init_warrior_info_panels()
        self.update_turn_display()

    def ask_world_size(self):
        while True:
            size = simpledialog.askinteger("World Size", "Enter board size (8-32):", minvalue=8, maxvalue=32)
            if size:
                return size
            messagebox.showwarning("Invalid Input", "Please enter a valid size between 8 and 32.")
    
    def update_resources(self):
        total_warriors = sum(len(player.warriors) for player in self.players)
        for player in self.players:
            player.resources += 10 + total_warriors

    def next_turn(self):
        if not self.players[self.current_player_index].eliminated and self.current_player_actions < 2:
            if not messagebox.askyesno("Pass Turn", "Do you want to end your turn?"):
                return  # Eğer kullanıcı elini pas geçmek istemiyorsa sıra değişmez
        current_player = self.players[self.current_player_index]
        if current_player.passed_turns >= 3 or not current_player.warriors:
            if(current_player.eliminated == False):
                self.eliminate_player(current_player)  
        self.current_player_actions = 0     
        while True:
            self.current_player_index = (self.current_player_index + 1) % self.player_count
            if not self.players[self.current_player_index].eliminated:
                break  # Eğer oyuncu elenmediyse, döngüyü kır ve sırayı ona ver
        if self.current_player_index == 0:  # Yeni bir tur başladı
            self.update_resources()
            self.make_attacks()
            self.remove_dead_warriors()
        self.update_warrior_info_panels()
        self.update_turn_display()
        self.refresh_board()  # Tahtayı güncelle
        self.check_victory()

    def make_attacks(self):
        print("saldırıyor")
        all_warriors = [warrior for player in self.players for warrior in player.warriors]
        for player in self.players:
            if not player.eliminated:
                for warrior in player.warriors:
                    warrior.perform_action(all_warriors,self.world_size)

    def clear_isolated_cells(self, x, y, player_color):
        # Belirli bir hücrenin komşularını kontrol et ve izole edilmiş hücreleri temizle
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue  # Kendi hücresini atla
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.world_size and 0 <= ny < self.world_size):
                    continue  # Hücre sınırlar içinde değilse atla
                cell = self.cells[(nx, ny)]
                if cell.cget('bg') == player_color:
                    # Etrafta aynı renkten başka bir savaşçı var mı kontrol et
                    if not any(warrior for player in self.players 
                               for warrior in player.warriors 
                               if warrior.x == nx and warrior.y == ny):
                        cell.config(text='.',bg='white')

    def remove_dead_warriors(self):
        for player in self.players:
            for warrior in player.warriors:
                if warrior.health <= 0:
                    self.cells[warrior.x, warrior.y].config(text='.', bg="white")
                    # Savaşçının öldüğü hücrenin çevresindeki hücreleri temizle
                    self.clear_isolated_cells(warrior.x, warrior.y, self.get_warrior_color(player.player_id))
        
        for player in self.players:
            player.warriors = [warrior for warrior in player.warriors if warrior.health > 0]
     
    def init_warrior_info_panels(self):
        # Oyuncu bilgi panellerini yatay olarak oluştur
        self.warrior_info_frame = tk.Frame(self.master)
        self.warrior_info_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        for player_id in range(1, self.player_count + 1):
            frame = tk.Frame(self.warrior_info_frame)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.warrior_info_panels[player_id] = frame
            label = tk.Label(frame, text=f"Player {player_id}", padx=5, pady=5)
            label.pack(side=tk.TOP)

    def update_warrior_info_panels(self):
        # Her oyuncu için savaşçı bilgilerini yatay olarak güncelle
        for player_id, frame in self.warrior_info_panels.items():
        # Önceki bilgileri temizle
            for widget in frame.winfo_children():
                widget.destroy()

            # Oyuncu başlığını yeniden oluştur
            label = tk.Label(frame, text=f"Player {player_id}", padx=5, pady=5)
            label.pack(side=tk.TOP)

            # Yeni bilgileri ekle
            player = self.players[player_id - 1]
            for warrior in player.warriors:
                info_text = f"{warrior.name} Health: {warrior.health}, Pos: ({warrior.x}, {warrior.y})"
                label = tk.Label(frame, text=info_text)
                label.pack(side=tk.TOP)  # Yukarı doğru uzamasını sağlar

        self.master.update_idletasks()

    def pass_turn(self):
        # Oyuncunun turunu pas geçmesi işlemleri
        current_player = self.players[self.current_player_index]
        current_player.passed_turns += 1
        if current_player.passed_turns >= 3:
            self.eliminate_player(current_player)
        else:
            self.next_turn()

    def eliminate_player(self, player):
        # Oyuncuyu oyun dışı bırak ve oyun alanını temizle
        player.eliminated = True
        for x, y in self.cells:
            cell_button = self.cells[(x, y)]
            if cell_button.cget("bg") == self.get_warrior_color(player.player_id):
                cell_button.config(text='.', bg='white')
        player.warriors.clear()  # Oyuncunun savaşçı listesini temizle
        messagebox.showinfo("Player Eliminated", f"Player {player.player_id} has been eliminated.")
        self.next_turn()
        

    def check_game_over_conditions(self):
        # Oyunun bitip bitmediğini kontrol et
        for player in self.players:
            if not player.warriors or player.passed_turns >= 3:
                self.eliminate_player(player)

    def check_victory(self):
        # Tüm hücrelerin sahibini kontrol et ve oyuncuların ele geçirdiği alanları hesapla
        ownership_count = {player_id: 0 for player_id in range(1, self.player_count + 1)}
        total_cells = self.world_size * self.world_size
        for player in self.players:
            if not player.eliminated:
                for warrior in player.warriors:
                    ownership_count[player.player_id] += 1

        # Oyunun kazananını kontrol et
        for player_id, count in ownership_count.items():
            if count >= total_cells * 0.6:
                # Bir oyuncu %60'tan fazla alana sahipse, oyunu kazanır
                self.declare_winner(player_id)
                return True

        # Eğer oyun alanında sadece bir oyuncu kaldıysa, o oyuncu kazanır
        active_players = [player for player in self.players if not player.eliminated]
        if len(active_players) == 1:
            self.declare_winner(active_players[0].player_id)
            return True
        
        return False  # Henüz bir kazanan yok

    def declare_winner(self, player_id):
        # Oyunun kazananını ilan et ve bilgilendirme yap
        messagebox.showinfo("Game Over", f"Player {player_id} has won the game!")
        self.master.quit()  # Oyun penceresini kapat
    
    def update_turn_display(self):
        # Sıradaki oyuncuyu gösteren metni güncelle
        turn_text = f"Player {self.current_player_index + 1}'s Turn"
        self.turn_label.config(text=turn_text)
        
    def ask_player_count(self):
        while True:
            count = simpledialog.askinteger("Player Count", "Enter number of players (1-4):", minvalue=1, maxvalue=4)
            if count:
                return count
            messagebox.showwarning("Invalid Input", "Please enter a valid player count between 1 and 4.")

    def init_gui(self):
        self.create_board()
        for row in range(self.world_size):
            for col in range(self.world_size):
                cell_key = (row, col)
                cell_button = self.cells[cell_key]
                cell_button.config(text='.', bg='white') 
        self.initialize_guardians()
       
    def initialize_guardians(self):


        corners = [(0, 0), (0, self.world_size-1), (self.world_size-1, 0), (self.world_size-1, self.world_size-1)]
        colors = ["red", "blue", "green", "yellow"]
        # Her oyuncu için rastgele bir köşeye "Muhafız" yerleştir
        # Bu örnek, tüm oyuncular için sabit pozisyonları kullanır, rastgelelik için düzenlenebilir
        self.create_player_info_panel()
        for i in range(self.player_count):
                guard = Guardian(self.players[i].player_id)
                row, col = corners[i]
                guard.x = row
                guard.y = col
                self.players[i].add_warrior(guard)
        self.refresh_board()
                

    def place_warrior(self, x, y, warrior):
    # Belirtilen konumda savaşçı yerleştirebilme kontrolü
        cell_key = (x, y)
        if cell_key in self.cells:
            button = self.cells[cell_key]
            current_color = button.cget("bg")
            player_color = self.get_warrior_color(warrior.player_id)
            
            # Oyuncunun sadece kendi renkleri üzerine veya beyaz hücrelere asker yerleştirebilmesi kontrolü
            if current_color == player_color :
                # Eğer bu hücrede zaten bir savaşçı varsa ve farklı bir türse, kaynakların %80'ini geri ver
                for player in self.players:
                    for existing_warrior in player.warriors:
                        if existing_warrior.x == x and existing_warrior.y == y and existing_warrior.name != warrior.name:
                            # Kaynakları geri al ve mevcut savaşçıyı listeden çıkar
                            player.resources += int(existing_warrior.cost * 0.8)
                            player.warriors.remove(existing_warrior)
                            #self.players[warrior.player_id - 1].warriors.append(warrior)
                            break
                button.config(text=warrior.name[0], bg=player_color)  # Savaşçının ilk harfi ve rengi ile güncelle
                warrior.x, warrior.y = x, y  # Savaşçının konumunu güncelle

                # Yerleştirilen savaşçının etrafındaki hücreleri boyama
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        adjacent_cell_key = (x + dr, y + dc)
                        if adjacent_cell_key in self.cells and (dr != 0 or dc != 0) and (self.cells[adjacent_cell_key]["bg"] == "white"):
                            self.cells[adjacent_cell_key].config(bg=player_color)
                return True
        return False
    
    def refresh_board(self):
        # Oyun tahtasındaki ve oyuncu bilgilerindeki değişiklikleri güncelle
        # Varsayılan durumu sıfırla
                
        # Eğer bu konumda bir savaşçı varsa, onu görselleştir
        for player in self.players:
            for warrior in player.warriors:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        new_x, new_y = warrior.x + dx, warrior.y + dy
                        # Eğer hücre tahta dışında değilse ve boşsa, rengini değiştir
                        if 0 <= new_x < self.world_size and 0 <= new_y < self.world_size and (self.cells[new_x, new_y]["bg"] == "white"):
                            self.cells[new_x, new_y].config(bg=self.get_warrior_color(player.player_id))
                self.cells[warrior.x,warrior.y].config(text=warrior.name[0] + str(warrior.player_id) , bg=self.get_warrior_color(player.player_id))        
                    

        # Oyuncu bilgilerini güncelle
        for i, player in enumerate(self.players):
            self.player_info_labels[i].config(text=f'Player {i+1}: Health: {player.health}, Resources: {player.resources}')
            
    def get_warrior_color(self, player_id):
        # Oyuncu ID'sine göre renk döndür
        colors = {1: "red", 2: "blue", 3: "green", 4: "yellow"}
        return colors.get(player_id, "grey")  # Eğer ID tanımsızsa gri döndür
    
    def create_player_info_panel(self):
        # Oyuncu bilgileri panelini oluştur
        self.info_panel = tk.Frame(self.master)
        self.info_panel.pack(fill=tk.X)

        # Oyuncu bilgilerini göstermek için Label widget'ları oluştur
        self.player_info_labels = []
        for i in range(self.player_count):
            label = tk.Label(self.info_panel, text=f'Player {i+1}: Health: '+ str(self.players[i].health) + ', Resources: ' +str(self.players[i].resources))  # Örnek değerler
            label.pack(side=tk.LEFT)
            self.player_info_labels.append(label)

    def create_board(self):
        board_frame = tk.Frame(self.master)
        board_frame.pack()

        for row in range(self.world_size):
            for col in range(self.world_size):
                cell = tk.Button(board_frame, text='', width=4, height=2, command=lambda r=row, c=col: self.cell_clicked(r, c))
                cell.grid(row=row, column=col, sticky='nsew')
                self.cells[(row, col)] = cell

        # Grid hücrelerinin boyutunu eşitler
        for i in range(self.world_size):
            board_frame.grid_rowconfigure(i, weight=1)
            board_frame.grid_columnconfigure(i, weight=1)

    def cell_clicked(self, row, col):
        # Bu metod, bir hücreye tıklandığında çağrılır.
        def on_warrior_selected(selection_window):
            if self.current_player_actions >= 2:
                messagebox.showinfo("Action Limit", "You have already made 2 actions this turn.")
                return  # Eğer oyuncu bu elde zaten 2 eylem yaptıysa, yeni eylem yapamaz
            warrior_type = warrior_type_var.get()
            selection_window.destroy()
            if warrior_type != "Select warrior type":
                # Seçilen savaşçı türüne göre işlem yap
                current_player = self.players[self.current_player_index]
                created = current_player.create_warrior(warrior_type, row, col, self)
               
                if created:
                    self.current_player_actions += 1 
                    self.refresh_board()  # Tahtayı ve oyuncu bilgilerini güncelle
                    self.next_turn()
                    current_player.passed_turns = 0
                else:
                    messagebox.showwarning("Invalid Action", "Warrior could not be placed.")
            

        if self.current_player_actions >= 2:
            messagebox.showinfo("Action Limit", "You have already made 2 actions this turn.")
            return  # Eğer oyuncu bu elde zaten 2 eylem yaptıysa, yeni eylem yapamaz
        # Savaşçı seçim penceresini oluştur
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Select Warrior Type")
        
        warrior_type_var = tk.StringVar(selection_window)
        warrior_type_var.set("Select warrior type")  # Varsayılan değer

        warrior_options = ["Guardian", "Archer", "Cannon", "Cavalry", "Medic"]
        warrior_menu = tk.OptionMenu(selection_window, warrior_type_var, *warrior_options)
        warrior_menu.pack()

        select_button = tk.Button(selection_window, text="Select", command=lambda: on_warrior_selected(selection_window))
        select_button.pack()
def main():
    root = tk.Tk()
    root.withdraw()
    app = GameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

