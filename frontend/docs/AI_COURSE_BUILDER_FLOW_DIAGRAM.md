# AI Course Builder Flow Diagram

## Overview

This document provides a visual representation of the AI Course Builder workflow and component interactions.

```mermaid
graph TD
    A[Instructor Dashboard] -->|Select Create with AI| B[AI Course Builder]
    B --> C{Initialize Builder}
    C -->|Success| D[Basic Information Form]
    C -->|Error| C1[Error Boundary]
    C1 -->|Retry| C
    C1 -->|Use Mock| D

    D -->|Submit| E[Learning Objectives Form]
    E -->|Submit| F[Generate Course Outline]

    F -->|API Request| G{AI Service}
    G -->|Success| H[Display Course Outline]
    G -->|Error| G1[Fall back to Mock]
    G1 --> H

    H -->|Continue| I[Generate Module Content]
    I -->|API Request| J{AI Service}
    J -->|Success| K[Display Module Content]
    J -->|Error| J1[Fall back to Mock]
    J1 --> K

    K -->|Continue| L[Content Enhancement]
    L -->|API Request| M{AI Service}
    M -->|Success| N[Display Enhanced Content]
    M -->|Error| M1[Fall back to Mock]
    M1 --> N

    N -->|Continue| O[Course Finalization]
    O -->|Complete| P[Save Course to Database]
    P --> Q[Redirect to Course Dashboard]
```

## Component Interaction

```mermaid
sequenceDiagram
    participant I as Instructor
    participant CB as AICourseBuilder
    participant BS as AIBuilderStore
    participant API as AICourseBuilderAPI
    participant AI as AI Service
    participant DB as Database

    I->>CB: Start AI Course Builder
    CB->>BS: initializeBuilder()
    BS->>API: initialize()

    alt Mock Mode Enabled
        API-->>BS: Return mock data
    else API Mode
        API->>AI: Connect to AI service
        AI-->>API: Connection status

        alt API Connection Failed
            API-->>BS: Fall back to mock data
        else API Connection Success
            API-->>BS: Return initialization data
        end
    end

    BS-->>CB: Builder initialized
    CB-->>I: Show step 1 (Basic Info)

    I->>CB: Submit basic info
    CB->>BS: updateBasicInfo()
    BS-->>CB: State updated
    CB-->>I: Show step 2 (Objectives)

    I->>CB: Submit objectives
    CB->>BS: updateObjectives()
    BS-->>CB: State updated
    CB-->>I: Show outline generation

    CB->>API: generateCourseOutline()

    alt Mock Mode
        API-->>CB: Return mock outline
    else API Mode
        API->>AI: Generate course outline
        AI-->>API: Course outline data
        API-->>CB: Return outline data
    end

    CB-->>I: Show generated outline

    Note over I,DB: Process continues through all phases...

    I->>CB: Complete course
    CB->>BS: completeCourseCreation()
    BS->>DB: Save course data
    DB-->>BS: Course saved
    BS-->>CB: Redirect to dashboard
    CB-->>I: Show course dashboard
```

## State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Initialization

    Initialization --> BasicInfo: Initialize Success
    Initialization --> Error: Initialize Failure
    Error --> Initialization: Retry
    Error --> MockMode: Use Mock Data
    MockMode --> BasicInfo

    BasicInfo --> LearningObjectives: Next
    LearningObjectives --> CourseOutlineGeneration: Next

    CourseOutlineGeneration --> OutlineReview: Generation Complete
    CourseOutlineGeneration --> Error: Generation Failure
    Error --> CourseOutlineGeneration: Retry

    OutlineReview --> ModuleContentGeneration: Next
    ModuleContentGeneration --> ModuleReview: Generation Complete
    ModuleContentGeneration --> Error: Generation Failure
    Error --> ModuleContentGeneration: Retry

    ModuleReview --> ContentEnhancement: Next
    ContentEnhancement --> FinalReview: Enhancement Complete
    ContentEnhancement --> Error: Enhancement Failure
    Error --> ContentEnhancement: Retry

    FinalReview --> CourseComplete: Save Course
    CourseComplete --> [*]
```

## Data Flow

```mermaid
flowchart TD
    subgraph Input
        A1[Course Title]
        A2[Description]
        A3[Category]
        A4[Level]
        A5[Learning Objectives]
    end

    subgraph "AI Processing"
        B1[Process Input]
        B2[Generate Outline]
        B3[Create Modules]
        B4[Create Lessons]
        B5[Enhance Content]
    end

    subgraph Output
        C1[Course Structure]
        C2[Module Content]
        C3[Lesson Materials]
        C4[Assessments]
        C5[Final Course]
    end

    A1 & A2 & A3 & A4 & A5 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> B3
    B3 --> C2
    B3 --> B4
    B4 --> C3
    B4 --> B5
    B5 --> C4
    C1 & C2 & C3 & C4 --> C5
```

## Mock API Mode Behavior

```mermaid
flowchart LR
    A[API Request] --> B{Mock Mode?}
    B -->|Yes| C[Return Mock Data]
    B -->|No| D{API Available?}
    D -->|Yes| E[Return Real Data]
    D -->|No| F{Development?}
    F -->|Yes| C
    F -->|No| G[Return Error]
```

This diagram illustrates how the AI Course Builder handles API requests in different scenarios, including the automatic fallback to mock responses during development.
