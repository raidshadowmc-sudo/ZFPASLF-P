from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
from app import app, db
from models import Player, Quest, PlayerQuest, Achievement, PlayerAchievement, CustomTitle, PlayerTitle, GradientTheme, PlayerGradientSetting
import os
import csv
import io
from datetime import datetime

# Admin password
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Minekillfire13!')

@app.route('/')
def index():
    """Display the enhanced leaderboard"""
    sort_by = request.args.get('sort', 'experience')
    search = request.args.get('search', '').strip()
    limit = min(int(request.args.get('limit', 50)), 200)

    if search:
        players = Player.search_players(search)[:limit]
    else:
        players = Player.get_leaderboard(sort_by=sort_by, limit=limit)

    is_admin = session.get('is_admin', False)
    stats = Player.get_statistics()

    return render_template('index.html', 
                         players=players, 
                         current_sort=sort_by,
                         search_query=search,
                         is_admin=is_admin,
                         stats=stats,
                         limit=limit)

@app.route('/player/<int:player_id>')
def player_profile(player_id):
    """Display detailed player profile"""
    player = Player.query.get_or_404(player_id)
    is_admin = session.get('is_admin', False)

    return render_template('player_profile.html', 
                         player=player, 
                         is_admin=is_admin)

@app.route('/statistics')
def statistics():
    """Display detailed statistics page"""
    stats = Player.get_statistics()
    top_players = {
        'experience': Player.get_leaderboard('experience', 5),
        'kills': Player.get_leaderboard('kills', 5),
        'final_kills': Player.get_leaderboard('final_kills', 5),
        'beds_broken': Player.get_leaderboard('beds_broken', 5),
        'wins': Player.get_leaderboard('wins', 5)
    }

    is_admin = session.get('is_admin', False)

    return render_template('statistics.html', 
                         stats=stats, 
                         top_players=top_players,
                         is_admin=is_admin)

@app.route('/admin')
def admin():
    """Admin panel"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен! Требуется авторизация администратора.', 'error')
        return redirect(url_for('login'))

    stats = Player.get_statistics()
    recent_players = Player.query.order_by(Player.created_at.desc()).limit(10).all()

    return render_template('admin.html', 
                         stats=stats, 
                         recent_players=recent_players)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Добро пожаловать, администратор!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Неверный пароль!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Admin logout"""
    session.pop('is_admin', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/player_login', methods=['GET', 'POST'])
def player_login():
    """Player login page"""
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        if nickname:
            player = Player.query.filter_by(nickname=nickname).first()
            if player:
                session['player_nickname'] = nickname
                flash(f'Добро пожаловать, {nickname}!', 'success')
                return redirect(url_for('quests'))
            else:
                flash('Игрок с таким ником не найден!', 'error')
        else:
            flash('Введите ваш игровой ник!', 'error')

    return render_template('player_login.html')

@app.route('/player_logout')
def player_logout():
    """Player logout"""
    player_name = session.get('player_nickname', '')
    session.pop('player_nickname', None)
    flash(f'До свидания, {player_name}!', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_player():
    """Add a new player to the leaderboard (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен! Только администратор может добавлять игроков.', 'error')
        return redirect(url_for('index'))

    try:
        # Basic fields
        nickname = request.form.get('nickname', '').strip()
        kills = request.form.get('kills', type=int, default=0)
        final_kills = request.form.get('final_kills', type=int, default=0)
        deaths = request.form.get('deaths', type=int, default=0)
        beds_broken = request.form.get('beds_broken', type=int, default=0)
        games_played = request.form.get('games_played', type=int, default=0)
        wins = request.form.get('wins', type=int, default=0)
        experience = request.form.get('experience', type=int, default=0)
        role = request.form.get('role', '').strip() or 'Игрок'
        if role == 'custom':
            custom_role = request.form.get('custom_role', '').strip()
            role = custom_role if custom_role else 'Игрок'
        server_ip = request.form.get('server_ip', '').strip()

        # Enhanced fields
        iron_collected = request.form.get('iron_collected', type=int, default=0)
        gold_collected = request.form.get('gold_collected', type=int, default=0)
        diamond_collected = request.form.get('diamond_collected', type=int, default=0)
        emerald_collected = request.form.get('emerald_collected', type=int, default=0)
        items_purchased = request.form.get('items_purchased', type=int, default=0)

        # Skin fields
        skin_type = request.form.get('skin_type', 'auto')
        is_premium = request.form.get('is_premium') == 'on'

        # Validation
        if not nickname:
            flash('Ник не может быть пустым!', 'error')
            return redirect(url_for('admin'))

        if len(nickname) > 20:
            flash('Ник не может быть длиннее 20 символов!', 'error')
            return redirect(url_for('admin'))

        # Check if player already exists
        existing_player = Player.query.filter_by(nickname=nickname).first()
        if existing_player:
            flash(f'Игрок с ником {nickname} уже существует!', 'error')
            return redirect(url_for('admin'))

        # Validate numeric fields
        numeric_fields = [
            ('киллы', kills), ('финальные киллы', final_kills),
            ('смерти', deaths), ('кровати', beds_broken),
            ('игры', games_played), ('победы', wins), ('опыт', experience),
            ('железо', iron_collected), ('золото', gold_collected),
            ('алмазы', diamond_collected), ('изумруды', emerald_collected),
            ('покупки', items_purchased)
        ]

        for field_name, value in numeric_fields:
            if value is None or value < 0:
                flash(f'{field_name.capitalize()} должны быть неотрицательным числом!', 'error')
                return redirect(url_for('admin'))
            if value > 999999:
                flash(f'{field_name.capitalize()} не могут превышать 999,999!', 'error')
                return redirect(url_for('admin'))

        # Logical validation
        if wins > games_played:
            flash('Количество побед не может превышать количество игр!', 'error')
            return redirect(url_for('admin'))

        # Add player
        player = Player.add_player(
            nickname=nickname, kills=kills, final_kills=final_kills,
            deaths=deaths, beds_broken=beds_broken, games_played=games_played,
            wins=wins, experience=experience, role=role, server_ip=server_ip,
            iron_collected=iron_collected, gold_collected=gold_collected,
            diamond_collected=diamond_collected, emerald_collected=emerald_collected,
            items_purchased=items_purchased
        )

        # Set skin settings
        if player:
            player.skin_type = skin_type
            player.is_premium = is_premium
            db.session.commit()

        flash(f'Игрок {nickname} успешно добавлен в таблицу лидеров!', 'success')

    except Exception as e:
        app.logger.error(f"Error adding player: {e}")
        flash('Произошла ошибка при добавлении игрока!', 'error')

    return redirect(url_for('admin'))

@app.route('/edit/<int:player_id>', methods=['POST'])
def edit_player(player_id):
    """Edit player statistics (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))

    player = Player.query.get_or_404(player_id)

    try:
        # Update fields
        player.kills = request.form.get('kills', type=int, default=player.kills)
        player.final_kills = request.form.get('final_kills', type=int, default=player.final_kills)
        player.deaths = request.form.get('deaths', type=int, default=player.deaths)
        player.beds_broken = request.form.get('beds_broken', type=int, default=player.beds_broken)
        player.games_played = request.form.get('games_played', type=int, default=player.games_played)
        player.wins = request.form.get('wins', type=int, default=player.wins)
        player.experience = request.form.get('experience', type=int, default=player.experience)
        player.role = request.form.get('role', default=player.role)
        player.server_ip = request.form.get('server_ip', default=player.server_ip)

        # Enhanced fields
        player.iron_collected = request.form.get('iron_collected', type=int, default=player.iron_collected)
        player.gold_collected = request.form.get('gold_collected', type=int, default=player.gold_collected)
        player.diamond_collected = request.form.get('diamond_collected', type=int, default=player.diamond_collected)
        player.emerald_collected = request.form.get('emerald_collected', type=int, default=player.emerald_collected)
        player.items_purchased = request.form.get('items_purchased', type=int, default=player.items_purchased)

        player.last_updated = datetime.utcnow()
        db.session.commit()

        # Check for new achievements
        from models import Achievement
        new_achievements = Achievement.check_player_achievements(player)

        success_message = f'Статистика игрока {player.nickname} обновлена!'
        if new_achievements:
            achievement_names = [a.title for a in new_achievements]
            success_message += f' Получены достижения: {", ".join(achievement_names)}'

        flash(success_message, 'success')

    except Exception as e:
        app.logger.error(f"Error editing player: {e}")
        flash('Произошла ошибка при редактировании игрока!', 'error')

    return redirect(url_for('player_profile', player_id=player_id))

@app.route('/modify/<int:player_id>', methods=['POST'])
def modify_player_stats(player_id):
    """Modify player statistics by adding/subtracting values (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))

    player = Player.query.get_or_404(player_id)

    try:
        operation = request.form.get('operation', 'add')  # 'add' or 'subtract'
        changes_made = []

        # Define stat fields and their names for logging
        stat_fields = {
            'kills': 'киллы',
            'final_kills': 'финальные киллы', 
            'deaths': 'смерти',
            'beds_broken': 'кровати',
            'games_played': 'игры',
            'wins': 'победы',
            'experience': 'опыт',
            'iron_collected': 'железо',
            'gold_collected': 'золото',
            'diamond_collected': 'алмазы',
            'emerald_collected': 'изумруды',
            'items_purchased': 'покупки'
        }

        for field, display_name in stat_fields.items():
            value = request.form.get(field, type=int)
            if value and value != 0:
                current_value = getattr(player, field, 0)

                if operation == 'add':
                    new_value = current_value + value
                    changes_made.append(f"+{value} {display_name}")
                else:  # subtract
                    new_value = max(0, current_value - value)  # Не даем опускаться ниже 0
                    changes_made.append(f"-{value} {display_name}")

                setattr(player, field, new_value)

        if changes_made:
            player.last_updated = datetime.utcnow()
            db.session.commit()

            operation_text = "Добавлено" if operation == 'add' else "Вычтено"
            flash(f'{operation_text} для {player.nickname}: {", ".join(changes_made)}', 'success')
        else:
            flash('Нет изменений для применения!', 'warning')

    except Exception as e:
        app.logger.error(f"Error modifying player stats: {e}")
        flash('Произошла ошибка при изменении статистики!', 'error')

    return redirect(url_for('player_profile', player_id=player_id))

@app.route('/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    """Delete a player (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))

    try:
        player = Player.query.get_or_404(player_id)
        nickname = player.nickname
        db.session.delete(player)
        db.session.commit()
        flash(f'Игрок {nickname} удален из таблицы лидеров!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting player: {e}")
        flash('Произошла ошибка при удалении игрока!', 'error')

    return redirect(url_for('admin'))

@app.route('/clear', methods=['POST'])
def clear_leaderboard():
    """Clear all players from the leaderboard (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен! Только администратор может очистить таблицу.', 'error')
        return redirect(url_for('index'))

    try:
        Player.query.delete()
        db.session.commit()
        flash('Таблица лидеров очищена!', 'success')
    except Exception as e:
        app.logger.error(f"Error clearing leaderboard: {e}")
        flash('Произошла ошибка при очистке таблицы!', 'error')

    return redirect(url_for('admin'))

@app.route('/export')
def export_leaderboard():
    """Export leaderboard data as CSV"""
    try:
        players = Player.query.order_by(Player.experience.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Ник', 'Уровень', 'Опыт', 'Киллы', 'Финальные киллы', 'Смерти',
            'K/D', 'FK/D', 'Кровати', 'Игры', 'Победы', 'Процент побед',
            'Роль', 'Сервер', 'Железо', 'Золото', 'Алмазы', 'Изумруды',
            'Покупки', 'Дата создания', 'Последнее обновление'
        ])

        # Data
        for player in players:
            writer.writerow([
                player.nickname, player.level, player.experience,
                player.kills, player.final_kills, player.deaths,
                player.kd_ratio, player.fkd_ratio, player.beds_broken,
                player.games_played, player.wins, player.win_rate,
                player.role, player.server_ip, player.iron_collected,
                player.gold_collected, player.diamond_collected,
                player.emerald_collected, player.items_purchased,
                player.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                player.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            ])

        output.seek(0)

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=bedwars_leaderboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        return response

    except Exception as e:
        app.logger.error(f"Error exporting data: {e}")
        flash('Произошла ошибка при экспорте данных!', 'error')
        return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics data (for charts)"""
    try:
        stats = Player.get_statistics()
        top_players = Player.get_leaderboard('experience', 10)

        # Prepare data for charts
        chart_data = {
            'player_levels': {},
            'top_players_exp': {
                'labels': [p.nickname for p in top_players],
                'data': [p.experience for p in top_players]
            },
            'top_players_kills': {
                'labels': [p.nickname for p in top_players],
                'data': [p.kills for p in top_players]
            }
        }

        # Level distribution
        all_players = Player.query.all()
        for player in all_players:
            level = f"Level {player.level}"
            chart_data['player_levels'][level] = chart_data['player_levels'].get(level, 0) + 1

        # Convert top_player to dict if it exists
        stats_copy = stats.copy()
        if stats_copy.get('top_player'):
            top_player = stats_copy['top_player']
            stats_copy['top_player'] = {
                'nickname': top_player.nickname,
                'level': top_player.level,
                'experience': top_player.experience,
                'kills': top_player.kills,
                'wins': top_player.wins
            }

        return jsonify({
            'stats': stats_copy,
            'charts': chart_data
        })

    except Exception as e:
        app.logger.error(f"Error getting API stats: {e}")
        return jsonify({'error': 'Failed to load statistics'}), 500

# Quest system routes
@app.route('/quests')
def quests():
    """Display quest system page"""
    is_admin = session.get('is_admin', False)
    current_player = None

    # Check if player is logged in
    player_nickname = session.get('player_nickname')
    if player_nickname:
        current_player = Player.query.filter_by(nickname=player_nickname).first()

    # Initialize default quests if none exist
    if Quest.query.count() == 0:
        Quest.create_default_quests()

    # Get all active quests
    active_quests = Quest.get_active_quests()

    # Get player quest progress if logged in
    player_progress = {}

    if current_player:
        # Update quest progress for current player
        PlayerQuest.update_player_quest_progress(current_player)

        # Get player's quest progress
        for quest in active_quests:
            player_quest = PlayerQuest.query.filter_by(
                player_id=current_player.id, 
                quest_id=quest.id
            ).first()

            if player_quest:
                player_progress[quest.id] = player_quest

    return render_template('quests.html', 
                         quests=active_quests,
                         player_progress=player_progress,
                         current_player=current_player,
                         is_admin=is_admin)

@app.route('/achievements')
def achievements():
    """Display achievements page"""
    is_admin = session.get('is_admin', False)
    current_player = None

    # Check if player is logged in
    player_nickname = session.get('player_nickname')
    if player_nickname:
        current_player = Player.query.filter_by(nickname=player_nickname).first()

    # Initialize default achievements if none exist
    if Achievement.query.count() == 0:
        Achievement.create_default_achievements()

    all_achievements = Achievement.query.all()

    # Get player achievements if logged in
    player_achievements = []

    if current_player:
        player_achievements = PlayerAchievement.query.filter_by(
            player_id=current_player.id
        ).all()

    return render_template('achievements.html',
                         achievements=all_achievements,
                         player_achievements=player_achievements,
                         current_player=current_player,
                         is_admin=is_admin)

@app.route('/quest/<int:quest_id>/accept', methods=['POST'])
def accept_quest(quest_id):
    """Accept a quest (player must be logged in)"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        flash('Необходимо войти в систему для принятия квестов!', 'error')
        return redirect(url_for('player_login'))

    try:
        player = Player.query.filter_by(nickname=player_nickname).first_or_404()
        quest = Quest.query.get_or_404(quest_id)

        # Check if quest already accepted
        existing_quest = PlayerQuest.query.filter_by(
            player_id=player.id,
            quest_id=quest_id
        ).first()

        if existing_quest and existing_quest.is_accepted:
            flash('Квест уже принят!', 'warning')
            return redirect(url_for('quests'))

        if not existing_quest:
            existing_quest = PlayerQuest()
            existing_quest.player_id = player.id
            existing_quest.quest_id = quest_id
            db.session.add(existing_quest)

        # Accept the quest and set baseline
        existing_quest.is_accepted = True
        existing_quest.accepted_at = datetime.utcnow()
        existing_quest.started_at = datetime.utcnow()

        # Set baseline value for quest tracking
        quest = Quest.query.get_or_404(quest_id)
        existing_quest.baseline_value = getattr(player, quest.type, 0)

        db.session.commit()
        flash(f'Квест "{quest.title}" принят!', 'success')

    except Exception as e:
        app.logger.error(f"Error accepting quest: {e}")
        flash('Ошибка при принятии квеста!', 'error')

    return redirect(url_for('quests'))

@app.route('/quest/<int:quest_id>/complete', methods=['POST'])
def complete_quest(quest_id):
    """Mark a quest as completed (admin only for demo)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('quests'))

    try:
        quest = Quest.query.get_or_404(quest_id)
        sample_player = Player.query.first()

        if not sample_player:
            flash('Нет игроков для демонстрации!', 'error')
            return redirect(url_for('quests'))

        # Get or create player quest
        player_quest = PlayerQuest.query.filter_by(
            player_id=sample_player.id,
            quest_id=quest_id
        ).first()

        if not player_quest:
            player_quest = PlayerQuest()
            player_quest.player_id = sample_player.id
            player_quest.quest_id = quest_id
            player_quest.is_accepted = True
            player_quest.accepted_at = datetime.utcnow()
            db.session.add(player_quest)

        # Complete the quest
        if not player_quest.is_completed:
            player_quest.is_completed = True
            player_quest.completed_at = datetime.utcnow()
            player_quest.current_progress = quest.target_value

            # Award rewards
            sample_player.experience += quest.reward_xp
            if quest.reward_title:
                sample_player.role = quest.reward_title

            db.session.commit()
            flash(f'Квест "{quest.title}" выполнен! Получено {quest.reward_xp} XP!', 'success')
        else:
            flash('Квест уже выполнен!', 'warning')

    except Exception as e:
        app.logger.error(f"Error completing quest: {e}")
        flash('Ошибка при выполнении квеста!', 'error')

    return redirect(url_for('quests'))

@app.route('/admin/quests')
def admin_quests():
    """Admin quest management"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    quests = Quest.query.all()
    quest_stats = []

    for quest in quests:
        total_attempts = PlayerQuest.query.filter_by(quest_id=quest.id).count()
        completed = PlayerQuest.query.filter_by(quest_id=quest.id, is_completed=True).count()
        completion_rate = (completed / total_attempts * 100) if total_attempts > 0 else 0

        quest_stats.append({
            'quest': quest,
            'total_attempts': total_attempts,
            'completed': completed,
            'completion_rate': completion_rate
        })

    return render_template('admin_quests.html', quest_stats=quest_stats)

@app.route('/init_demo', methods=['POST'])
def init_demo():
    """Initialize demo data (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        # Create demo players if they don't exist
        demo_players = [
            {
                'nickname': 'ProGamer2024',
                'kills': 150,
                'final_kills': 45,
                'deaths': 75,
                'beds_broken': 28,
                'games_played': 85,
                'wins': 52,
                'experience': 8500,
                'role': 'Опытный игрок',
                'iron_collected': 5000,
                'gold_collected': 2500,
                'diamond_collected': 800,
                'emerald_collected': 150,
                'items_purchased': 500
            },
            {
                'nickname': 'BedDestroyer',
                'kills': 89,
                'final_kills': 22,
                'deaths': 45,
                'beds_broken': 65,
                'games_played': 72,
                'wins': 38,
                'experience': 5200,
                'role': 'Разрушитель',
                'iron_collected': 3200,
                'gold_collected': 1800,
                'diamond_collected': 450,
                'emerald_collected': 85,
                'items_purchased': 320
            },
            {
                'nickname': 'NewbieFighter',
                'kills': 25,
                'final_kills': 8,
                'deaths': 32,
                'beds_broken': 12,
                'games_played': 35,
                'wins': 15,
                'experience': 1800,
                'role': 'Новичок',
                'iron_collected': 1200,
                'gold_collected': 600,
                'diamond_collected': 120,
                'emerald_collected': 25,
                'items_purchased': 150
            }
        ]

        for player_data in demo_players:
            existing = Player.query.filter_by(nickname=player_data['nickname']).first()
            if not existing:
                Player.add_player(**player_data)

        # Initialize quests and achievements
        Quest.create_default_quests()
        Achievement.create_default_achievements()
        CustomTitle.create_default_titles()
        GradientTheme.create_default_themes()

        # Update quest progress for all players
        players = Player.query.all()
        for player in players:
            PlayerQuest.update_player_quest_progress(player)

        flash('Демо-данные успешно инициализированы!', 'success')

    except Exception as e:
        app.logger.error(f"Error initializing demo data: {e}")
        flash('Ошибка при инициализации демо-данных!', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/update_skin/<int:player_id>', methods=['POST'])
def update_player_skin(player_id):
    """Update player skin settings (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    player = Player.query.get_or_404(player_id)

    try:
        skin_type = request.form.get('skin_type', 'auto')
        namemc_url = request.form.get('namemc_url', '').strip()
        is_premium = request.form.get('is_premium') == 'on'

        player.is_premium = is_premium

        if skin_type == 'custom' and namemc_url:
            if player.set_custom_skin(namemc_url):
                flash(f'Кастомный скин установлен для {player.nickname}!', 'success')
            else:
                flash('Ошибка при установке кастомного скина!', 'error')
        else:
            player.skin_type = skin_type
            player.skin_url = None
            flash(f'Тип скина изменен на {skin_type} для {player.nickname}!', 'success')

        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error updating player skin: {e}")
        flash('Ошибка при обновлении скина!', 'error')

    return redirect(url_for('player_profile', player_id=player_id))

@app.route('/admin/generate_quests', methods=['POST'])
def generate_quests():
    """Generate periodic quests (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        quest_type = data.get('type', 'daily') if data else 'daily'
        quests_data = []

        if quest_type == 'daily':
            quests_data = [
                {'title': 'Ежедневный убийца', 'description': 'Убейте 10 игроков', 'type': 'kills', 'target_value': 10, 'difficulty': 'easy', 'reward_xp': 100},
                {'title': 'Разрушитель кроватей', 'description': 'Сломайте 3 кровати', 'type': 'beds_broken', 'target_value': 3, 'difficulty': 'medium', 'reward_xp': 200},
                {'title': 'Победитель дня', 'description': 'Выиграйте 2 игры', 'type': 'wins', 'target_value': 2, 'difficulty': 'medium', 'reward_xp': 150}
            ]
        elif quest_type == 'weekly':
            quests_data =[
                {'title': 'Еженедельный воин', 'description': 'Убейте 100 игроков за неделю', 'type': 'kills', 'target_value': 100, 'difficulty': 'hard', 'reward_xp': 500},
                {'title': 'Мастер финальных убийств', 'description': 'Совершите 25 финальных убийств', 'type': 'final_kills', 'target_value': 25, 'difficulty': 'hard', 'reward_xp': 600},
                {'title': 'Недельный чемпион', 'description': 'Выиграйте 15 игр за неделю', 'type': 'wins', 'target_value': 15, 'difficulty': 'epic', 'reward_xp': 800}
            ]
        elif quest_type == 'monthly':
            quests_data = [
                {'title': 'Легенда месяца', 'description': 'Убейте 500 игроков за месяц', 'type': 'kills', 'target_value': 500, 'difficulty': 'epic', 'reward_xp': 2000},
                {'title': 'Разрушитель империй', 'description': 'Сломайте 100 кроватей за месяц', 'type': 'beds_broken', 'target_value': 100, 'difficulty': 'epic', 'reward_xp': 1800},
                {'title': 'Непобедимый', 'description': 'Выиграйте 50 игр за месяц', 'type': 'wins', 'target_value': 50, 'difficulty': 'epic', 'reward_xp': 2500, 'reward_title': 'Непобедимый'}
            ]

        # Create new quests
        for quest_data in quests_data:
            quest = Quest(**quest_data)
            db.session.add(quest)

        db.session.commit()
        return jsonify({'success': True, 'message': f'{quest_type.capitalize()} квесты созданы!'})

    except Exception as e:
        app.logger.error(f"Error generating {quest_type} quests: {e}")
        return jsonify({'error': 'Failed to generate quests'}), 500

@app.route('/admin/create_quest', methods=['POST'])  
def create_quest():
    """Create custom quest (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        target_value = request.form.get('target_value', '0')
        reward_experience = request.form.get('reward_experience', '0')

        quest_data = {
            'title': title,
            'description': description,
            'type': request.form.get('quest_type'),
            'difficulty': request.form.get('difficulty'),
            'target_value': int(target_value) if target_value.isdigit() else 0,
            'reward_xp': int(reward_experience) if reward_experience.isdigit() else 0,
            'reward_title': request.form.get('reward_title', '').strip() or None
        }

        quest = Quest(**quest_data)
        db.session.add(quest)
        db.session.commit()

        flash(f'Квест "{quest_data["title"]}" успешно создан!', 'success')

    except Exception as e:
        app.logger.error(f"Error creating quest: {e}")
        flash('Ошибка при создании квеста!', 'error')

    return redirect(url_for('admin_quests'))

@app.route('/admin/delete_quest/<int:quest_id>', methods=['DELETE'])
def delete_quest(quest_id):
    """Delete quest (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        quest = Quest.query.get_or_404(quest_id)
        # Delete related player quests first
        PlayerQuest.query.filter_by(quest_id=quest_id).delete()
        db.session.delete(quest)
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error deleting quest: {e}")
        return jsonify({'error': 'Failed to delete quest'}), 500

@app.route('/admin/reset_quest/<int:quest_id>', methods=['POST'])
def reset_quest_progress(quest_id):
    """Reset quest progress for all players (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        PlayerQuest.query.filter_by(quest_id=quest_id).delete()
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error resetting quest progress: {e}")
        return jsonify({'error': 'Failed to reset quest progress'}), 500

@app.route('/admin/titles')
def admin_titles():
    """Admin titles management"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    titles = CustomTitle.query.all()
    players = Player.query.all()

    return render_template('admin_titles.html', titles=titles, players=players)

@app.route('/admin/create_title', methods=['POST'])
def create_title():
    """Create custom title (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        name = request.form.get('name', '').strip().lower()
        display_name = request.form.get('display_name', '').strip()
        color = request.form.get('color', '#ffd700')
        glow_color = request.form.get('glow_color', color)

        if not name or not display_name:
            flash('Название и отображаемое имя обязательны!', 'error')
            return redirect(url_for('admin_titles'))

        # Check if title already exists
        existing = CustomTitle.query.filter_by(name=name).first()
        if existing:
            flash('Титул с таким названием уже существует!', 'error')
            return redirect(url_for('admin_titles'))

        title = CustomTitle(
            name=name,
            display_name=display_name,
            color=color,
            glow_color=glow_color
        )

        db.session.add(title)
        db.session.commit()

        flash(f'Титул "{display_name}" успешно создан!', 'success')

    except Exception as e:
        app.logger.error(f"Error creating title: {e}")
        flash('Ошибка при создании титула!', 'error')

    return redirect(url_for('admin_titles'))

@app.route('/admin/assign_title', methods=['POST'])
def assign_title():
    """Assign title to player (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        player_id = request.form.get('player_id', type=int)
        title_id = request.form.get('title_id', type=int)

        if not player_id or not title_id:
            flash('Выберите игрока и титул!', 'error')
            return redirect(url_for('admin_titles'))

        player = Player.query.get_or_404(player_id)
        title = CustomTitle.query.get_or_404(title_id)

        # Remove any existing active title
        PlayerTitle.query.filter_by(player_id=player_id, is_active=True).update({'is_active': False})

        # Add new title
        player_title = PlayerTitle(
            player_id=player_id,
            title_id=title_id,
            is_active=True
        )

        db.session.add(player_title)
        db.session.commit()

        flash(f'Титул "{title.display_name}" присвоен игроку {player.nickname}!', 'success')

    except Exception as e:
        app.logger.error(f"Error assigning title: {e}")
        flash('Ошибка при присвоении титула!', 'error')

    return redirect(url_for('admin_titles'))

@app.route('/admin/remove_title/<int:player_id>', methods=['POST'])
def remove_title(player_id):
    """Remove title from player (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        PlayerTitle.query.filter_by(player_id=player_id, is_active=True).update({'is_active': False})
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error removing title: {e}")
        return jsonify({'error': 'Failed to remove title'}), 500

@app.route('/admin/remove_all_titles', methods=['POST'])
def remove_all_titles():
    """Remove all custom titles from all players (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        PlayerTitle.query.update({'is_active': False})
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error removing all titles: {e}")
        return jsonify({'error': 'Failed to remove all titles'}), 500

@app.route('/admin/gradients')
def admin_gradients():
    """Admin gradient management"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    # Initialize default themes if none exist
    if GradientTheme.query.count() == 0:
        GradientTheme.create_default_themes()

    themes = GradientTheme.query.all()
    players = Player.query.all()

    # Group themes by element type
    grouped_themes = {}
    for theme in themes:
        if theme.element_type not in grouped_themes:
            grouped_themes[theme.element_type] = []
        grouped_themes[theme.element_type].append(theme)

    return render_template('admin_gradients.html', 
                         grouped_themes=grouped_themes, 
                         players=players)

@app.route('/admin/create_gradient', methods=['POST'])
def create_gradient():
    """Create new gradient theme (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        name = request.form.get('name', '').strip().lower().replace(' ', '_')
        display_name = request.form.get('display_name', '').strip()
        element_type = request.form.get('element_type', '').strip()
        color1 = request.form.get('color1', '#ffffff')
        color2 = request.form.get('color2', '#000000')
        color3 = request.form.get('color3', '').strip() or None
        gradient_direction = request.form.get('gradient_direction', '45deg')
        animation_enabled = request.form.get('animation_enabled') == 'on'

        if not name or not display_name or not element_type:
            flash('Все обязательные поля должны быть заполнены!', 'error')
            return redirect(url_for('admin_gradients'))

        # Check if theme already exists
        existing = GradientTheme.query.filter_by(name=name).first()
        if existing:
            flash('Градиент с таким названием уже существует!', 'error')
            return redirect(url_for('admin_gradients'))

        theme = GradientTheme(
            name=name,
            display_name=display_name,
            element_type=element_type,
            color1=color1,
            color2=color2,
            color3=color3,
            gradient_direction=gradient_direction,
            animation_enabled=animation_enabled
        )

        db.session.add(theme)
        db.session.commit()

        flash(f'Градиент "{display_name}" успешно создан!', 'success')

    except Exception as e:
        app.logger.error(f"Error creating gradient: {e}")
        flash('Ошибка при создании градиента!', 'error')

    return redirect(url_for('admin_gradients'))

@app.route('/admin/assign_gradient', methods=['POST'])
def assign_gradient():
    """Assign gradient to player (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        player_id = request.form.get('player_id', type=int)
        element_type = request.form.get('element_type', '').strip()
        gradient_theme_id = request.form.get('gradient_theme_id', type=int)
        custom_color1 = request.form.get('custom_color1', '').strip() or None
        custom_color2 = request.form.get('custom_color2', '').strip() or None
        custom_color3 = request.form.get('custom_color3', '').strip() or None

        if not player_id or not element_type:
            flash('Выберите игрока и тип элемента!', 'error')
            return redirect(url_for('admin_gradients'))

        player = Player.query.get_or_404(player_id)

        # Remove existing gradient for this element type
        PlayerGradientSetting.query.filter_by(
            player_id=player_id,
            element_type=element_type
        ).delete()

        # Create new gradient setting
        gradient_setting = PlayerGradientSetting(
            player_id=player_id,
            element_type=element_type,
            gradient_theme_id=gradient_theme_id if gradient_theme_id else None,
            custom_color1=custom_color1,
            custom_color2=custom_color2,
            custom_color3=custom_color3,
            is_enabled=True
        )

        db.session.add(gradient_setting)
        db.session.commit()

        theme_name = "кастомный градиент"
        if gradient_theme_id:
            theme = GradientTheme.query.get(gradient_theme_id)
            theme_name = theme.display_name if theme else "градиент"

        flash(f'Градиент "{theme_name}" присвоен игроку {player.nickname} для {element_type}!', 'success')

    except Exception as e:
        app.logger.error(f"Error assigning gradient: {e}")
        flash('Ошибка при присвоении градиента!', 'error')

    return redirect(url_for('admin_gradients'))

@app.route('/admin/remove_gradient/<int:player_id>/<element_type>', methods=['POST'])
def remove_gradient(player_id, element_type):
    """Remove gradient from player (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        PlayerGradientSetting.query.filter_by(
            player_id=player_id,
            element_type=element_type
        ).delete()
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error removing gradient: {e}")
        return jsonify({'error': 'Failed to remove gradient'}), 500

@app.route('/profile/<nickname>')
def public_profile(nickname):
    """Display public player profile"""
    player = Player.query.filter_by(nickname=nickname).first_or_404()

    if not player.profile_is_public and session.get('player_nickname') != nickname:
        flash('Профиль этого игрока приватный!', 'error')
        return redirect(url_for('index'))

    is_owner = session.get('player_nickname') == nickname
    is_admin = session.get('is_admin', False)

    return render_template('public_profile.html', 
                         player=player, 
                         is_owner=is_owner,
                         is_admin=is_admin)

@app.route('/my-profile')
def my_profile():
    """Display and edit current player's profile"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        flash('Необходимо войти в систему для доступа к профилю!', 'error')
        return redirect(url_for('player_login'))

    player = Player.query.filter_by(nickname=player_nickname).first_or_404()

    # Get available gradient themes
    gradient_themes = {}
    themes = GradientTheme.query.filter_by(is_active=True).all()
    for theme in themes:
        if theme.element_type not in gradient_themes:
            gradient_themes[theme.element_type] = []
        gradient_themes[theme.element_type].append(theme)

    return render_template('my_profile.html', 
                         player=player,
                         gradient_themes=gradient_themes)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Update current player's profile"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        flash('Необходимо войти в систему!', 'error')
        return redirect(url_for('player_login'))

    player = Player.query.filter_by(nickname=player_nickname).first_or_404()

    try:
        # Update personal information
        player.real_name = request.form.get('real_name', '').strip() or None
        player.bio = request.form.get('bio', '').strip() or None
        player.discord_tag = request.form.get('discord_tag', '').strip() or None
        player.youtube_channel = request.form.get('youtube_channel', '').strip() or None
        player.twitch_channel = request.form.get('twitch_channel', '').strip() or None
        player.favorite_server = request.form.get('favorite_server', '').strip() or None
        player.favorite_map = request.form.get('favorite_map', '').strip() or None
        player.preferred_gamemode = request.form.get('preferred_gamemode', '').strip() or None
        player.profile_banner_color = request.form.get('profile_banner_color', '#3498db')
        player.profile_is_public = request.form.get('profile_is_public') == 'on'
        player.custom_status = request.form.get('custom_status', '').strip() or None
        player.location = request.form.get('location', '').strip() or None

        # Handle birthday
        birthday_str = request.form.get('birthday', '').strip()
        if birthday_str:
            from datetime import datetime
            try:
                player.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
            except ValueError:
                player.birthday = None
        else:
            player.birthday = None

        # Handle custom avatar and banner
        player.custom_avatar_url = request.form.get('custom_avatar_url', '').strip() or None

        # Only allow banner customization for level 20+
        if player.level >= 20:
            player.custom_banner_url = request.form.get('custom_banner_url', '').strip() or None
            player.banner_is_animated = request.form.get('banner_is_animated') == 'on'

        # Profile section colors
        player.stats_section_color = request.form.get('stats_section_color', '#343a40')
        player.info_section_color = request.form.get('info_section_color', '#343a40')
        player.social_section_color = request.form.get('social_section_color', '#343a40')
        player.prefs_section_color = request.form.get('prefs_section_color', '#343a40')

        # Handle extended social networks
        social_types = request.form.getlist('social_type[]')
        social_values = request.form.getlist('social_value[]')

        if social_types and social_values:
            social_networks = []
            for i, (social_type, social_value) in enumerate(zip(social_types, social_values)):
                if social_type and social_value.strip():
                    social_networks.append({
                        'type': social_type,
                        'value': social_value.strip()
                    })
            player.set_social_networks_list(social_networks)
        else:
            player.set_social_networks_list([])

        db.session.commit()
        flash('Профиль успешно обновлен!', 'success')

    except Exception as e:
        app.logger.error(f"Error updating profile: {e}")
        flash('Ошибка при обновлении профиля!', 'error')

    return redirect(url_for('my_profile'))

@app.route('/apply-gradient', methods=['POST'])
def apply_gradient():
    """Apply gradient to player's elements"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        return jsonify({'error': 'Unauthorized'}), 403

    player = Player.query.filter_by(nickname=player_nickname).first_or_404()

    try:
        element_type = request.form.get('element_type')
        gradient_theme_id = request.form.get('gradient_theme_id', type=int)

        if not element_type:
            return jsonify({'error': 'Element type required'}), 400

        # Remove existing gradient for this element type
        PlayerGradientSetting.query.filter_by(
            player_id=player.id,
            element_type=element_type
        ).delete()

        # Add new gradient if theme selected
        if gradient_theme_id:
            gradient_setting = PlayerGradientSetting(
                player_id=player.id,
                element_type=element_type,
                gradient_theme_id=gradient_theme_id,
                is_enabled=True
            )
            db.session.add(gradient_setting)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error applying gradient: {e}")
        return jsonify({'error': 'Failed to apply gradient'}), 500

@app.route('/update-player-role', methods=['POST'])
def update_player_role():
    """Update player's current role"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        flash('Необходимо войти в систему!', 'error')
        return redirect(url_for('player_login'))

    player = Player.query.filter_by(nickname=player_nickname).first_or_404()

    try:
        new_role = request.form.get('new_role', '').strip()
        if new_role:
            player.role = new_role
            db.session.commit()
            flash(f'Роль изменена на "{new_role}"!', 'success')

    except Exception as e:
        app.logger.error(f"Error updating role: {e}")
        flash('Ошибка при изменении роли!', 'error')

    return redirect(url_for('my_profile'))

@app.route('/activate-player-title', methods=['POST'])
def activate_player_title():
    """Activate a specific title for player"""
    player_nickname = session.get('player_nickname')
    if not player_nickname:
        flash('Необходимо войти в систему!', 'error')
        return redirect(url_for('player_login'))

    player = Player.query.filter_by(nickname=player_nickname).first_or_404()

    try:
        title_id = request.form.get('title_id', type=int)

        if title_id:
            # Deactivate all current titles
            PlayerTitle.query.filter_by(player_id=player.id, is_active=True).update({'is_active': False})

            # Activate the selected title
            player_title = PlayerTitle.query.filter_by(player_id=player.id, title_id=title_id).first()
            if player_title:
                player_title.is_active = True
                db.session.commit()
                flash('Титул активирован!', 'success')
            else:
                flash('Титул не найден!', 'error')

    except Exception as e:
        app.logger.error(f"Error activating title: {e}")
        flash('Ошибка при активации титула!', 'error')

    return redirect(url_for('my_profile'))

@app.route('/admin/achievements')
def admin_achievements():
    """Admin achievements management page"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    achievements = Achievement.query.all()

    # Add earned count to each achievement
    for achievement in achievements:
        achievement.earned_count = PlayerAchievement.query.filter_by(achievement_id=achievement.id).count()

    return render_template('admin_achievements.html', achievements=achievements)

@app.route('/admin/create_achievement', methods=['POST'])
def create_achievement():
    """Create custom achievement (admin only)"""
    if not session.get('is_admin', False):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('login'))

    try:
        import json

        # Validate input fields
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        condition_type = request.form.get('condition_type', '').strip()
        condition_value = request.form.get('condition_value', '0')

        if not title or not description or not condition_type:
            flash('Название, описание и тип условия обязательны!', 'error')
            return redirect(url_for('admin_achievements'))

        # Create proper JSON condition
        try:
            condition_val = int(condition_value) if condition_value.isdigit() else 0
        except:
            condition_val = 0

        unlock_condition = json.dumps({condition_type: condition_val})

        achievement_data = {
            'title': title,
            'description': description,
            'unlock_condition': unlock_condition,
            'rarity': request.form.get('rarity', 'common'),
            'reward_xp': int(request.form.get('reward_xp', 0)),
            'reward_title': request.form.get('reward_title', '').strip() or None,
            'icon': request.form.get('icon', '').strip() or 'fas fa-star',
            'is_hidden': request.form.get('is_hidden') == 'on'
        }

        achievement = Achievement(**achievement_data)
        db.session.add(achievement)
        db.session.commit()

        flash(f'Достижение "{achievement_data["title"]}" успешно создано!', 'success')

    except Exception as e:
        app.logger.error(f"Error creating achievement: {e}")
        flash('Ошибка при создании достижения!', 'error')

    return redirect(url_for('admin_achievements'))

@app.route('/admin/generate_achievements', methods=['POST'])
def generate_achievements():
    """Generate seasonal achievements (admin only)"""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        import json

        seasonal_achievements = [
            {
                'title': 'Новогодний воин',
                'description': 'Убейте 100 игроков в зимнем сезоне',
                'unlock_condition': json.dumps({"kills": 100}),
                'rarity': 'epic',
                'reward_xp': 1000,
                'reward_title': 'Зимний воин',
                'icon': 'fas fa-snowflake',
                'is_hidden': False
            },
            {
                'title': 'Летний чемпион',
                'description': 'Выиграйте 50 игр летом',
                'unlock_condition': json.dumps({"wins": 50}),
                'rarity': 'legendary',
                'reward_xp': 2000,
                'reward_title': 'Летняя легенда',
                'icon': 'fas fa-sun',
                'is_hidden': False
            },
            {
                'title': 'Коллекционер ресурсов',
                'description': 'Соберите 10000 единиц ресурсов',
                'unlock_condition': json.dumps({"total_resources": 10000}),
                'rarity': 'rare',
                'reward_xp': 750,
                'reward_title': 'Мастер ресурсов',
                'icon': 'fas fa-gem',
                'is_hidden': True
            },
            {
                'title': 'Весенний освободитель',
                'description': 'Сломайте 25 кроватей весной',
                'unlock_condition': json.dumps({"beds_broken": 25}),
                'rarity': 'rare',
                'reward_xp': 800,
                'reward_title': 'Весенний разрушитель',
                'icon': 'fas fa-leaf',
                'is_hidden': False
            },
            {
                'title': 'Осенний стратег',
                'description': 'Достигните 70% процента побед',
                'unlock_condition': json.dumps({"win_rate": 70.0}),
                'rarity': 'legendary',
                'reward_xp': 1500,
                'reward_title': 'Мастер стратегии',
                'icon': 'fas fa-chess',
                'is_hidden': True
            }
        ]

        # Check if achievements already exist to avoid duplicates
        created_count = 0
        for achievement_data in seasonal_achievements:
            existing = Achievement.query.filter_by(title=achievement_data['title']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
                created_count += 1

        db.session.commit()

        if created_count > 0:
            return jsonify({'success': True, 'message': f'Создано {created_count} сезонных достижений!'})
        else:
            return jsonify({'success': True, 'message': 'Все сезонные достижения уже существуют!'})

    except Exception as e:
        app.logger.error(f"Error generating achievements: {e}")
        return jsonify({'error': f'Ошибка при создании достижений: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error_message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', error_message="Внутренняя ошибка сервера"), 500