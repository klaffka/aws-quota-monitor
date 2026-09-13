# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Broad AWS quota coverage through official CloudWatch usage metrics and paginated resource inventories.
- Offline quota coverage and package verification tools.
- Automated Python, packaging, and Terraform checks for pull requests and branches.
- Tag-driven GitHub releases with validated versions, release notes, and SHA-256 checksums.
- FinSpace Managed kdb measurements for 28 resource, node, and storage quotas.
- EC2 Image Builder measurements for 20 resource and configuration quotas.
- AWS Network Firewall measurements for 25 resource, policy, rule-group, TLS,
  VPC-endpoint, and container quotas.

### Changed

- Quota collection, alerting, reporting, and deployment behavior now use explicit failure and data-quality states.

### Fixed

- Historical quota measurements and monthly reports preserve account, Region, unit, and interval boundaries.
- Corrected the Network Firewall stateless-rule-group quota code.
