"""配置管理模块"""
import toml
import os
from pathlib import Path
from typing import Dict, Any
from threading import Lock


class Config:
    """配置管理类（带缓存和文件监控）"""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._last_modified: float = 0
        self._lock = Lock()
        self.load_config()
    
    def _should_reload(self) -> bool:
        """检查是否需要重新加载配置"""
        if not self.config_path.exists():
            return False
        
        current_modified = os.path.getmtime(self.config_path)
        return current_modified > self._last_modified
    
    def load_config(self) -> None:
        """加载配置文件（带缓存）"""
        with self._lock:
            if self.config_path.exists():
                # 只有在文件被修改时才重新加载
                if self._should_reload() or not self._config:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        self._config = toml.load(f)
                    self._last_modified = os.path.getmtime(self.config_path)
            else:
                raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键（自动重新加载配置）"""
        # 检查是否需要重新加载配置
        if self._should_reload():
            self.load_config()
            
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值并保存到文件"""
        keys = key.split('.')
        config = self._config
        
        # 导航到正确的嵌套位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存到文件
        self.save_config()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            toml.dump(self._config, f)
    
    @property
    def app(self) -> Dict[str, Any]:
        """应用配置"""
        return self.get('app', {})
    
    @property
    def wechat(self) -> Dict[str, Any]:
        """微信配置"""
        return self.get('wechat', {})
    
    @property
    def database(self) -> Dict[str, Any]:
        """数据库配置"""
        return self.get('database', {})
    
    @property
    def logging(self) -> Dict[str, Any]:
        """日志配置"""
        return self.get('logging', {})


# 全局配置实例
config = Config()
