package main

import (
	"fmt"
	"log"

	"github.com/visionik/vAgenda/api/go/pkg/builder"
	"github.com/visionik/vAgenda/api/go/pkg/core"
	"github.com/visionik/vAgenda/api/go/pkg/updater"
)

func main() {
	fmt.Println("=== vAgenda Mutation API Demo ===")
	fmt.Println()

	// Direct mutations on TodoList
	fmt.Println("1. Direct TodoList mutations:")
	todoList := &core.TodoList{}

	// Add items
	todoList.AddItem(core.TodoItem{Title: "Task 1", Status: core.StatusPending})
	todoList.AddItem(core.TodoItem{Title: "Task 2", Status: core.StatusPending})
	todoList.AddItem(core.TodoItem{Title: "Task 3", Status: core.StatusPending})
	fmt.Printf("   Added 3 items, total: %d\n", len(todoList.Items))

	// Update item
	err := todoList.UpdateItem(1, func(item *core.TodoItem) {
		item.Status = core.StatusCompleted
		item.Title = "Task 2 (updated)"
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Updated item 1: %s (%s)\n", todoList.Items[1].Title, todoList.Items[1].Status)

	// Find item
	item := todoList.FindItem(func(i *core.TodoItem) bool {
		return i.Status == core.StatusCompleted
	})
	if item != nil {
		fmt.Printf("   Found completed item: %s\n", item.Title)
	}

	// Remove item
	err = todoList.RemoveItem(0)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Removed item 0, remaining: %d\n\n", len(todoList.Items))

	// Direct mutations on Plan
	fmt.Println("2. Direct Plan mutations:")
	plan := &core.Plan{}

	// Add narratives
	plan.AddNarrative("overview", core.Narrative{
		Title:   "Overview",
		Content: "This is the project overview",
	})
	plan.AddNarrative("details", core.Narrative{
		Title:   "Details",
		Content: "Project details here",
	})
	fmt.Printf("   Added 2 narratives, total: %d\n", len(plan.Narratives))

	// Update narrative
	err = plan.UpdateNarrative("overview", func(n *core.Narrative) {
		n.Content = "Updated overview content"
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Updated narrative 'overview': %s\n", plan.Narratives["overview"].Content)

	// Add phases
	plan.AddPhase(core.Phase{Title: "Phase 1", Status: core.PhaseStatusPending})
	plan.AddPhase(core.Phase{Title: "Phase 2", Status: core.PhaseStatusPending})
	fmt.Printf("   Added 2 phases, total: %d\n", len(plan.Phases))

	// Update phase
	err = plan.UpdatePhase(0, func(p *core.Phase) {
		p.Status = core.PhaseStatusInProgress
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Updated phase 0: %s (%s)\n\n", plan.Phases[0].Title, plan.Phases[0].Status)

	// Validated mutations with Updater
	fmt.Println("3. Validated mutations with Updater:")

	// Create a document
	doc := builder.NewTodoList("1.0").
		WithAuthor("Demo User").
		WithDescription("Personal task list").
		AddItem("Write code", core.StatusPending).
		AddItem("Review PR", core.StatusPending).
		Build()

	// Create updater
	upd := updater.NewUpdater(doc)

	// Add item with validation
	err = upd.AddItemValidated(core.TodoItem{
		Title:  "Deploy to production",
		Status: core.StatusPending,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Added validated item, total: %d\n", len(doc.TodoList.Items))

	// Update item with validation
	err = upd.UpdateItemStatus(0, core.StatusCompleted)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Updated item 0 status: %s\n", doc.TodoList.Items[0].Status)

	// Try invalid mutation (wrong document type)
	invalidDoc := builder.NewPlan("My Plan", "1.0").
		WithDescription("A plan document").
		WithProposal("Proposal", "Required proposal content").
		Build()

	badUpd := updater.NewUpdater(invalidDoc)
	err = badUpd.AddItemValidated(core.TodoItem{Title: "Task", Status: core.StatusPending})
	if err != nil {
		fmt.Printf("   Validation caught error: %v\n\n", err)
	}

	fmt.Println("=== Demo complete ===")
}
