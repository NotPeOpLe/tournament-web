SELECT json_arrayagg(json_object('id', t.id, 'full_name', t.full_name, 'acronym', t.acronym, 'flag_name', t.flag_name, 'players', p.players)) AS json
FROM team t
LEFT JOIN
  (SELECT player.team AS id,
          json_arrayagg(json_object('id', player.id, 'team_id', player.team, 'user_id', player.user_id, 'username', player.username, 'register_date', player.register_date, 'info', player.info, 'bp1', player.bp1, 'active', player.active)) AS players
   FROM player
   GROUP BY player.team) p ON p.id = t.id
