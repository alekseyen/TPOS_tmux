# TPOS_tmux
Python script that start tmux session with --N jupyters notebook in individual directory(also create them)

To start use (don't forget install requirements in your env `pip install -r requirements.txt`):
```
python main.py start 5
```

To connect to the created session use:
```
tmux at -t YOUR_TMUX_SESSION_NAME (by default {username}tmux_session)
```

To stop each tmux pannel and delete folder use: 

```python main.py stop_all```
