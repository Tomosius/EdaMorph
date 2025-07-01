"""
SessionState for EdaMorph: Holds the current Polars DataFrame, metadata,
and user/session-specific settings.
"""

import polars as pl

class SessionState:
    """
    Manages the current session's data and runtime preferences.
    """
    def __init__(self):
        self.df = None                 # Current Polars DataFrame or LazyFrame
        self.df_name = None            # Name of loaded file
        self.df_path = None            # File path or upload info
        self.lazy = False              # If current df is lazy
        self.polars_mode = "eager"     # or "lazy"
        self.theme = "light"
        self.font = "default"
        # Add more user/session settings as needed

    def set_df(self, df, name=None, path=None, lazy=None):
        self.df = df
        if name is not None:
            self.df_name = name
        if path is not None:
            self.df_path = path
        if lazy is not None:
            self.lazy = lazy

    def clear(self):
        self.df = None
        self.df_name = None
        self.df_path = None
        self.lazy = False

session_state = SessionState()

