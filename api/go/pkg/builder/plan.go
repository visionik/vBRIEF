package builder

import "github.com/visionik/vBRIEF/api/go/pkg/core"

// PlanBuilder provides a fluent API for building Plan documents.
type PlanBuilder struct {
	doc *core.Document
}

// NewPlan creates a new Plan builder with the specified title and version.
func NewPlan(title, version string) *PlanBuilder {
	return NewPlanWithStatus(version, title, core.PlanStatusDraft)
}

// NewPlanWithStatus creates a new Plan builder with explicit status.
//
// This matches the intent of the original extension proposal (version, title, status).
func NewPlanWithStatus(version, title string, status core.PlanStatus) *PlanBuilder {
	return &PlanBuilder{
		doc: &core.Document{
			Info: core.Info{
				Version: version,
			},
			Plan: &core.Plan{
				Title:      title,
				Status:     status,
				Narratives: make(map[string]string),
			},
		},
	}
}

// WithAuthor sets the document author.
func (b *PlanBuilder) WithAuthor(author string) *PlanBuilder {
	b.doc.Info.Author = author
	return b
}

// WithDescription sets the document description.
func (b *PlanBuilder) WithDescription(description string) *PlanBuilder {
	b.doc.Info.Description = description
	return b
}

// WithStatus sets the plan status.
func (b *PlanBuilder) WithStatus(status core.PlanStatus) *PlanBuilder {
	b.doc.Plan.Status = status
	return b
}

// WithNarrative adds a narrative to the plan.
func (b *PlanBuilder) WithNarrative(key, content string) *PlanBuilder {
	b.doc.Plan.Narratives[key] = content
	return b
}

// WithProposal adds the required proposal narrative.
func (b *PlanBuilder) WithProposal(content string) *PlanBuilder {
	return b.WithNarrative("proposal", content)
}

// WithProblem adds a problem statement narrative.
func (b *PlanBuilder) WithProblem(content string) *PlanBuilder {
	return b.WithNarrative("problem", content)
}

// WithBackground adds a background narrative.
func (b *PlanBuilder) WithBackground(content string) *PlanBuilder {
	return b.WithNarrative("background", content)
}

// WithContext is an alias for WithBackground (kept for compatibility).
func (b *PlanBuilder) WithContext(content string) *PlanBuilder {
	return b.WithBackground(content)
}

// WithAlternative adds an alternative narrative.
func (b *PlanBuilder) WithAlternative(content string) *PlanBuilder {
	return b.WithNarrative("alternative", content)
}

// WithRisk adds a risk narrative.
func (b *PlanBuilder) WithRisk(content string) *PlanBuilder {
	return b.WithNarrative("risk", content)
}

// WithTest adds a test narrative.
func (b *PlanBuilder) WithTest(content string) *PlanBuilder {
	return b.WithNarrative("test", content)
}

// AddPlanItem adds a plan item to the plan.
func (b *PlanBuilder) AddPlanItem(title string, status core.PlanItemStatus) *PlanBuilder {
	item := core.PlanItem{
		Title:  title,
		Status: status,
	}
	b.doc.Plan.Items = append(b.doc.Plan.Items, item)
	return b
}

// AddPendingItem adds a pending plan item to the plan.
func (b *PlanBuilder) AddPendingItem(title string) *PlanBuilder {
	return b.AddPlanItem(title, core.PlanItemStatusPending)
}

// AddInProgressItem adds an in-progress plan item to the plan.
func (b *PlanBuilder) AddInProgressItem(title string) *PlanBuilder {
	return b.AddPlanItem(title, core.PlanItemStatusInProgress)
}

// AddCompletedItem adds a completed plan item to the plan.
func (b *PlanBuilder) AddCompletedItem(title string) *PlanBuilder {
	return b.AddPlanItem(title, core.PlanItemStatusCompleted)
}

// Build returns the constructed document.
func (b *PlanBuilder) Build() *core.Document {
	return b.doc
}
