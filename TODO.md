# Codebase Examiner Modularization Plan

## Overview

This document outlines the complete plan to transform the Codebase Examiner from a monolithic Python-focused tool into a modular, extensible system that supports multiple programming languages and analysis capabilities.

## Current State

The current system has a single `code_inspector.py` module that handles all Python code extraction using both runtime inspection and AST parsing. While functional, this approach has limitations:

- **Language-specific**: Only supports Python
- **Monolithic**: All extraction logic is in one place
- **Inflexible**: Hard to add new types of analysis
- **Fixed output**: Limited to predefined documentation formats

## Target Architecture

The new modular architecture will provide:

- **Pluggable extractors** for different programming languages
- **Specialized extractors** for different analysis types (metrics, dependencies, security, etc.)
- **Configurable output** with multiple renderer options
- **Registry system** for discovering and managing extractors
- **Clear interfaces** for third-party extractor development

## Implementation Plan

### Phase 1: Core Architecture (Foundation)

#### Task 1.1: Create BaseExtractor Interface
- **File**: `src/codebase_examiner/core/extractors/base.py`
- **Description**: Create abstract base class defining the extractor interface
- **Details**:
  - Abstract methods: `can_extract(file_path)`, `extract(file_path)`, `get_capabilities()`
  - Properties: `name`, `version`, `supported_extensions`
  - Base validation and error handling

#### Task 1.2: Define Extractor Capabilities
- **File**: `src/codebase_examiner/core/extractors/base.py`
- **Description**: Create enum for different extraction types
- **Details**:
  - `CODE_STRUCTURE`: Classes, functions, modules
  - `DEPENDENCIES`: Import analysis, dependency graphs
  - `METRICS`: Lines of code, complexity, test coverage
  - `SECURITY`: Vulnerability scanning, code quality
  - `DOCUMENTATION`: Docstring analysis, comment extraction
  - `STYLE`: Code formatting, linting issues

#### Task 2.1: Create ExtractedData Models
- **File**: `src/codebase_examiner/core/models.py`
- **Description**: Define base data structures for extractor output
- **Details**:
  - `ExtractedData` base class with common metadata
  - Polymorphic design to support different data types
  - JSON serialization support

#### Task 2.2: Move Documentation Models
- **File**: `src/codebase_examiner/core/models.py`
- **Description**: Relocate existing data models to centralized location
- **Details**:
  - Move `FunctionDocumentation`, `ClassDocumentation`, `ModuleDocumentation`
  - Update imports across the codebase
  - Inherit from `ExtractedData` base class

#### Task 2.3: Create ExtractionResult Model
- **File**: `src/codebase_examiner/core/models.py`
- **Description**: Container for results from multiple extractors
- **Details**:
  - Metadata: timestamp, extractors used, file counts
  - Data: list of `ExtractedData` objects
  - Methods for filtering by capability type

#### Task 3.1: Create Python Extractor File
- **File**: `src/codebase_examiner/core/extractors/python_extractor.py`
- **Description**: New file to house Python-specific extraction logic
- **Details**:
  - Implement `BaseExtractor` interface
  - Support for `.py` files
  - Capability: `CODE_STRUCTURE`

#### Task 3.2: Move Python Logic to Extractor
- **Description**: Refactor existing inspection functions into `PythonExtractor` class
- **Details**:
  - Move `inspect_module`, `inspect_function`, `inspect_class`
  - Convert to instance methods
  - Maintain existing functionality

#### Task 3.3: Move AST Logic to Extractor
- **Description**: Consolidate AST parsing within `PythonExtractor`
- **Details**:
  - Move `parse_module_with_ast`, `extract_function_info_from_ast`, `extract_class_info_from_ast`
  - Integrate with runtime inspection as fallback
  - Handle edge cases and error conditions

#### Task 4.1: Create Extractor Registry
- **File**: `src/codebase_examiner/core/registry.py`
- **Description**: Central system for managing extractors
- **Details**:
  - Singleton pattern for global registry
  - Thread-safe operations
  - Plugin discovery mechanism

#### Task 4.2: Implement Registry Methods
- **Description**: Core registry functionality
- **Details**:
  - `register_extractor(extractor)`: Add new extractor
  - `get_extractors_for_file(file_path)`: Find compatible extractors
  - `get_extractors_by_capability(capability)`: Filter by analysis type
  - `list_extractors()`: Get all registered extractors

#### Task 4.3: Setup Default Registry
- **Description**: Initialize registry with built-in extractors
- **Details**:
  - Register `PythonExtractor` by default
  - Create factory functions for common configurations
  - Environment-based configuration support

### Phase 2: Integration (Connecting Components)

#### Task 5.1: Update inspect_codebase Function
- **File**: `src/codebase_examiner/core/code_inspector.py`
- **Description**: Modify main inspection function to use registry
- **Details**:
  - Iterate through files and find compatible extractors
  - Coordinate extraction from multiple extractors per file
  - Aggregate results into `ExtractionResult`

#### Task 5.2: Create CodebaseInspector Class
- **File**: `src/codebase_examiner/core/code_inspector.py`
- **Description**: New class to orchestrate the inspection process
- **Details**:
  - Constructor accepts registry and configuration
  - Methods: `inspect_directory()`, `inspect_files()`
  - Progress reporting and error handling

#### Task 5.3: Update Return Types
- **Description**: Change function signatures throughout the codebase
- **Details**:
  - `inspect_codebase()` returns `ExtractionResult` instead of `List[ModuleDocumentation]`
  - Update all callers to handle new return type
  - Provide backward compatibility wrapper

#### Task 6.1: Update Doc Generator Input
- **File**: `src/codebase_examiner/core/doc_generator.py`
- **Description**: Modify to accept `ExtractionResult`
- **Details**:
  - Update `generate_documentation()` signature
  - Extract appropriate data based on output format
  - Handle mixed data types from different extractors

#### Task 6.2: Create Documentation Renderer Interface
- **File**: `src/codebase_examiner/core/renderers/base.py`
- **Description**: Abstract interface for output formatters
- **Details**:
  - Abstract methods: `render(extraction_result)`, `get_supported_formats()`
  - Base class with common utilities
  - Configuration support

#### Task 6.3: Create Renderer Implementations
- **Files**: 
  - `src/codebase_examiner/core/renderers/markdown_renderer.py`
  - `src/codebase_examiner/core/renderers/json_renderer.py`
- **Description**: Concrete renderer implementations
- **Details**:
  - `MarkdownRenderer`: Uses section generators for structured output
  - `JsonRenderer`: Direct serialization of extraction data
  - Extensible for future formats (HTML, PDF, etc.)

### Phase 3: User Interface (Exposing New Capabilities)

#### Task 7.1: Update Section Generator Base
- **File**: `src/codebase_examiner/core/section_generators.py`
- **Description**: Modify to work with `ExtractionResult`
- **Details**:
  - Update `SectionGenerator.generate()` signature
  - Add methods to filter data by capability
  - Maintain backward compatibility

#### Task 7.2: Create Code Structure Section
- **File**: `src/codebase_examiner/core/section_generators.py`
- **Description**: Dedicated section for code structure data
- **Details**:
  - Replaces current `ModulesSection`
  - Handles multiple programming languages
  - Configurable detail levels

#### Task 7.3: Create Extractor Summary Section
- **File**: `src/codebase_examiner/core/section_generators.py`
- **Description**: New section showing what analysis was performed
- **Details**:
  - Lists extractors used
  - Shows file counts by type
  - Includes extraction metadata

#### Task 8.1: Add CLI Extractor Option
- **File**: `src/codebase_examiner/cli.py`
- **Description**: Command-line options for extractor selection
- **Details**:
  - `--extractors`: Specify which extractors to use
  - `--capabilities`: Filter by capability type
  - Validation and error messages

#### Task 8.2: Add List Extractors Command
- **File**: `src/codebase_examiner/cli.py`
- **Description**: New command to show available extractors
- **Details**:
  - `codebase-examiner list-extractors`
  - Show name, version, capabilities, supported files
  - Optional filtering by capability

#### Task 8.3: Update Examiner Tool
- **File**: `src/codebase_examiner/core/examiner_tool.py`
- **Description**: Update MCP tool for new architecture
- **Details**:
  - Add extractor selection parameters
  - Update tool descriptor
  - Maintain API compatibility

### Phase 4: Testing & Examples (Quality & Demonstration)

#### Task 9.1: Update Code Inspector Tests
- **File**: `src/codebase_examiner/core/code_inspector_spec.py`
- **Description**: Adapt tests for new architecture
- **Details**:
  - Test `CodebaseInspector` class
  - Mock extractor registry
  - Verify `ExtractionResult` structure

#### Task 9.2: Create Python Extractor Tests
- **File**: `src/codebase_examiner/core/extractors/python_extractor_spec.py`
- **Description**: Comprehensive tests for Python extraction
- **Details**:
  - Test all extraction methods
  - Verify AST and runtime inspection
  - Error handling and edge cases

#### Task 9.3: Create Registry Tests
- **File**: `src/codebase_examiner/core/registry_spec.py`
- **Description**: Test extractor registration and discovery
- **Details**:
  - Registration and deregistration
  - File matching logic
  - Capability filtering

#### Task 9.4: Update Doc Generator Tests
- **File**: `src/codebase_examiner/core/doc_generator_spec.py`
- **Description**: Adapt for `ExtractionResult` input
- **Details**:
  - Create test `ExtractionResult` fixtures
  - Test multiple renderer types
  - Verify output format consistency

#### Task 9.5: Update CLI Tests
- **File**: `src/codebase_examiner/cli_spec.py`
- **Description**: Test new command-line options
- **Details**:
  - Test extractor selection
  - Test list-extractors command
  - Integration testing with new architecture

#### Task 10.1: Create Example Extractors
- **Description**: Demonstrate extensibility with practical examples
- **Details**:
  - Document extractor development process
  - Show different capability types
  - Provide templates for common use cases

#### Task 10.2: Create Metrics Extractor
- **File**: `src/codebase_examiner/core/extractors/metrics_extractor.py`
- **Description**: Example extractor for code metrics
- **Details**:
  - Lines of code, function count, class count
  - Cyclomatic complexity
  - Capability: `METRICS`

#### Task 10.3: Create Dependency Extractor
- **File**: `src/codebase_examiner/core/extractors/dependency_extractor.py`
- **Description**: Example extractor for dependency analysis
- **Details**:
  - Import statements and dependencies
  - Dependency graph generation
  - Capability: `DEPENDENCIES`

### Phase 5: Documentation & Release (Publishing Changes)

#### Task 11.1: Update README
- **File**: `README.md`
- **Description**: Document new modular architecture
- **Details**:
  - Add extractor concept explanation
  - Update usage examples
  - Add configuration options

#### Task 11.2: Create Extractor Guide
- **File**: `EXTRACTOR_GUIDE.md`
- **Description**: Developer guide for creating extractors
- **Details**:
  - Step-by-step extractor development
  - API reference for `BaseExtractor`
  - Best practices and patterns

#### Task 11.3: Update Specification
- **File**: `SPEC.md`
- **Description**: Update product specification
- **Details**:
  - Add modular architecture section
  - Update capability descriptions
  - Revise integration scenarios

#### Task 12.1: Ensure Backward Compatibility
- **Description**: Create compatibility layer for existing users
- **Details**:
  - Wrapper functions for old API
  - Default behavior matches current system
  - Clear migration path

#### Task 12.2: Add Deprecation Warnings
- **Description**: Notify users of API changes
- **Details**:
  - Warning messages for deprecated functions
  - Documentation of replacement APIs
  - Timeline for removal

#### Task 12.3: Prepare Release
- **Description**: Version update and release preparation
- **Details**:
  - Update version to indicate major change
  - Update CHANGELOG.md with new features
  - Prepare release notes

## Benefits of Modular Architecture

### For Users
- **Flexibility**: Choose which analysis to perform
- **Performance**: Run only needed extractors
- **Extensibility**: Add custom analysis without modifying core code
- **Language Support**: Easy addition of new programming languages

### For Developers
- **Separation of Concerns**: Clear boundaries between components
- **Testability**: Individual extractors can be tested in isolation
- **Maintainability**: Smaller, focused modules
- **Extensibility**: Plugin architecture enables community contributions

### For AI Agents
- **Targeted Analysis**: Request specific types of information
- **Efficient Processing**: Avoid unnecessary analysis
- **Rich Context**: Multiple perspectives on the same codebase
- **Scalability**: Process large codebases selectively

## Implementation Notes

### Design Principles
1. **Interface Segregation**: Small, focused interfaces
2. **Dependency Inversion**: Depend on abstractions, not concretions
3. **Open/Closed**: Open for extension, closed for modification
4. **Single Responsibility**: Each extractor has one clear purpose

### Error Handling
- Extractors should fail gracefully
- Registry should handle extractor failures
- Partial results should be preserved
- Clear error reporting to users

### Performance Considerations
- Lazy loading of extractors
- Parallel extraction when possible
- Caching of extraction results
- Memory-efficient data structures

### Configuration
- Environment variables for default extractors
- Configuration files for complex setups
- Command-line overrides
- Programmatic configuration API

## Migration Strategy

### Phase Implementation
The phases are designed to be implemented incrementally:
1. **Phase 1** establishes the foundation without breaking existing functionality
2. **Phase 2** integrates new components while maintaining backward compatibility
3. **Phase 3** exposes new capabilities to users
4. **Phase 4** ensures quality and provides examples
5. **Phase 5** completes the transition and prepares for release

### Risk Mitigation
- Comprehensive test coverage before changes
- Feature flags for gradual rollout
- Backward compatibility maintained throughout
- Clear rollback procedures

### Success Criteria
- All existing tests pass
- New functionality works as designed
- Performance is maintained or improved
- Documentation is complete and accurate
- Community can easily create new extractors

## Future Enhancements

### Additional Languages
- JavaScript/TypeScript extractor
- Java extractor
- C# extractor
- Go extractor

### Advanced Analysis
- Security vulnerability scanning
- Performance hotspot detection
- Test coverage analysis
- Documentation quality metrics

### Output Formats
- HTML with interactive features
- PDF reports
- GraphQL API
- REST API endpoints

### Integration
- IDE plugins
- CI/CD pipeline integration
- Git hooks
- Code review tools

---

This plan provides a complete roadmap for transforming the Codebase Examiner into a truly modular and extensible system while maintaining backward compatibility and ensuring a smooth transition for existing users.
