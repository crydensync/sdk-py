# crydensync-py - Python SDK

<div align="center">

[![Status](https://img.shields.io/badge/status-planning-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Go Version](https://img.shields.io/badge/go-1.21+-blue)]()

</div>

## 🔗 Quick Links
- [Documentation](https://docs.crydensync.com)
- [GitHub Organization](https://github.com/crydensync)
- [Core Repository](https://github.com/crydensync/cryden)
- [Report Bug](https://github.com/crydensync/cryden/issues)
- [Discord Community](https://discord.gg/crydensync) (coming soon)

## 🎯 Purpose
Pythonic interface for CrydenSync authentication.

## 📊 Status
- **Phase**: Planning
- **Progress**: 0%
- **Target**: After api v1.0.0

## 🗺️ Roadmap

### v1.0.0
- [ ] Sync client
- [ ] Async client
- [ ] Type hints
- [ ] Django integration
- [ ] Flask integration

### v1.1.0
- [ ] FastAPI integration
- [ ] CLI tools
- [ ] Session management

## 🔧 Development
```bash
pip install -e .
pytest
```

📦 Usage

```python
from crydensync import Cryden

cryden = Cryden('https://api.crydensync.com')
user = cryden.auth.sign_up(email, password)
```

🔗 Dependencies

· api HTTP endpoints

## 🆘 Getting Help

- **Documentation**: [docs.crydensync.com](https://docs.crydensync.com)
- **Issues**: [GitHub Issues](https://github.com/crydensync/cryden/issues)
- **Discussions**: [GitHub Discussions](https://github.com/crydensync/cryden/discussions)
- **Discord**: [Join our server](https://discord.gg/crydensync) (coming soon)

## 🤝 Contributing

We welcome contributions! Please:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check [open issues](https://github.com/crydensync/cryden/issues)
3. Join [Discord](https://discord.gg/crydensync)

**Current needs:**
- 🐛 Bug hunters
- 📝 Documentation writers
- 🧪 Testers
- 💡 Feature ideas

## 📄 License

MIT © [CrydenSync](https://github.com/crydensync)

**This is open source software. Use it freely, modify it, share it.**
