# BMMS Mode Switching Documentation

## Overview

This comprehensive guide explains how to switch between OBCMS (single-tenant) and BMMS (multi-tenant) modes in the OBCMS system. The BMMS implementation enables seamless transition between operational modes through configuration changes only - no code modifications required.

## Quick Reference

| Operation | Command | Time Required | Impact |
|-----------|---------|---------------|---------|
| **OBCMS → BMMS** | `cp .env.bmms .env && restart` | < 1 minute | Multi-tenant mode enabled |
| **BMMS → OBCMS** | `cp .env.obcms .env && restart` | < 1 minute | Single-tenant mode restored |
| **Check Mode** | `python manage.py shell -c "from obc_management.settings.bmms_config import is_bmms_mode; print('BMMS' if is_bmms_mode() else 'OBCMS')"` | < 10 seconds | Display current mode |

## Documentation Structure

1. **[Mode Switching Process](MODE_SWITCHING_PROCESS.md)** - Step-by-step instructions for switching modes
2. **[System Changes](SYSTEM_CHANGES.md)** - What changes occur when enabling BMMS mode
3. **[User Interface Changes](UI_CHANGES.md)** - Visual and navigation differences between modes
4. **[Security & Access Control](SECURITY_IMPLICATIONS.md)** - Security features and access control changes
5. **[Performance Considerations](PERFORMANCE_CONSIDERATIONS.md)** - Performance impact and optimization
6. **[Mode Comparison](MODE_COMPARISON.md)** - Detailed comparison of capabilities in each mode
7. **[Data Preservation](DATA_PRESERVATION.md)** - Data integrity and backward compatibility
8. **[Production Readiness](PRODUCTION_READINESS.md)** - Production deployment status and requirements

## Key Concepts

### OBCMS Mode (Current)
- **Single Tenant**: Serves only Office for Other Bangsamoro Communities (OOBC)
- **No URL Prefix**: Direct access to all features (e.g., `/communities/`)
- **Auto-injection**: OOBC organization automatically applied to all requests
- **Production Ready**: Currently deployed and operational

### BMMS Mode (Future)
- **Multi-Tenant**: Serves all 44 BARMM Ministries, Offices, and Agencies (MOAs)
- **URL Prefix**: Organization-specific URLs (e.g., `/moa/OOBC/communities/`, `/moa/MOH/communities/`)
- **Organization Switching**: Users can switch between authorized organizations
- **Configuration Ready**: Implemented and ready for staging deployment

## Architecture Highlights

```
Single Codebase → Dual Operation
├── OBCMS Mode: Single-tenant (OOBC only)
│   ├── URLs: /communities/, /mana/, /dashboard/
│   ├── Auto-inject: OOBC organization
│   └── No organization switching
└── BMMS Mode: Multi-tenant (44 MOAs)
    ├── URLs: /moa/<ORG>/communities/, /moa/<ORG>/mana/
    ├── URL-based: Organization from URL
    └── Organization switching allowed
```

## Implementation Status

- ✅ **Configuration Infrastructure**: Complete
- ✅ **Middleware Implementation**: Complete
- ✅ **Model Migration**: 42 models migrated (6,898 records)
- ✅ **View Layer Updates**: 95+ views organization-aware
- ✅ **Testing Infrastructure**: 36 test cases ready
- ✅ **Documentation**: Complete
- 🟡 **Production Readiness**: 85% (staging validation required)

## Getting Started

1. **Check Current Mode**:
   ```bash
   python manage.py shell -c "from obc_management.settings.bmms_config import is_bmms_mode; print('BMMS' if is_bmms_mode() else 'OBCMS')"
   ```

2. **Switch to BMMS Mode** (when ready):
   ```bash
   cp .env.bmms .env
   # Restart your application server
   ```

3. **Switch Back to OBCMS** (if needed):
   ```bash
   cp .env.obcms .env
   # Restart your application server
   ```

## Important Notes

- **Zero Downtime**: Mode switching requires only application restart
- **Data Preservation**: All data remains intact during mode switching
- **Backward Compatibility**: OBCMS mode operates exactly as before
- **Configuration Only**: No code changes required for mode switching

## Support

For questions or issues:
1. Check the detailed documentation in this folder
2. Review the [BMMS Implementation Guide](../IMPLEMENTATION_COMPLETE.md)
3. Contact the development team for assistance

---

**Last Updated**: October 14, 2025  
**Implementation Status**: Complete  
**Production Readiness**: 85% (Staging validation required)