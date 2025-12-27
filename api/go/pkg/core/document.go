package core

// Document manipulation methods for editing vAgenda documents after creation.

// AddTodoItem adds a new item to the TodoList.
// Returns an error if the document doesn't contain a TodoList.
func (d *Document) AddTodoItem(item TodoItem) error {
	if d.TodoList == nil {
		return ErrNoTodoList
	}
	d.TodoList.AddItem(item)
	return nil
}

// UpdateTodoItem updates an existing item at the specified index.
// Returns an error if the index is out of bounds.
func (d *Document) UpdateTodoItem(index int, item TodoItem) error {
	if d.TodoList == nil {
		return ErrNoTodoList
	}
	return d.TodoList.UpdateItem(index, func(existing *TodoItem) {
		*existing = item
	})
}

// UpdateTodoItemStatus updates the status of an item at the specified index.
func (d *Document) UpdateTodoItemStatus(index int, status ItemStatus) error {
	if d.TodoList == nil {
		return ErrNoTodoList
	}
	return d.TodoList.UpdateItem(index, func(item *TodoItem) {
		item.Status = status
	})
}

// RemoveTodoItem removes an item at the specified index.
func (d *Document) RemoveTodoItem(index int) error {
	if d.TodoList == nil {
		return ErrNoTodoList
	}
	return d.TodoList.RemoveItem(index)
}

// GetTodoItems returns all todo items (nil-safe).
func (d *Document) GetTodoItems() []TodoItem {
	if d.TodoList == nil {
		return nil
	}
	return d.TodoList.Items
}

// AddPhase adds a new phase to the Plan.
func (d *Document) AddPhase(phase Phase) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	d.Plan.Phases = append(d.Plan.Phases, phase)
	return nil
}

// UpdatePhase updates an existing phase at the specified index.
func (d *Document) UpdatePhase(index int, phase Phase) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Phases) {
		return ErrInvalidIndex
	}
	d.Plan.Phases[index] = phase
	return nil
}

// UpdatePhaseStatus updates the status of a phase at the specified index.
func (d *Document) UpdatePhaseStatus(index int, status PhaseStatus) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Phases) {
		return ErrInvalidIndex
	}
	d.Plan.Phases[index].Status = status
	return nil
}

// RemovePhase removes a phase at the specified index.
func (d *Document) RemovePhase(index int) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Phases) {
		return ErrInvalidIndex
	}
	d.Plan.Phases = append(d.Plan.Phases[:index], d.Plan.Phases[index+1:]...)
	return nil
}

// AddNarrative adds or updates a narrative in the Plan.
func (d *Document) AddNarrative(key string, narrative Narrative) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	if d.Plan.Narratives == nil {
		d.Plan.Narratives = make(map[string]Narrative)
	}
	d.Plan.Narratives[key] = narrative
	return nil
}

// RemoveNarrative removes a narrative from the Plan.
func (d *Document) RemoveNarrative(key string) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	delete(d.Plan.Narratives, key)
	return nil
}

// UpdatePlanStatus updates the status of the Plan.
func (d *Document) UpdatePlanStatus(status PlanStatus) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	d.Plan.Status = status
	return nil
}

// GetPhases returns all phases (nil-safe).
func (d *Document) GetPhases() []Phase {
	if d.Plan == nil {
		return nil
	}
	return d.Plan.Phases
}

// GetNarratives returns all narratives (nil-safe).
func (d *Document) GetNarratives() map[string]Narrative {
	if d.Plan == nil {
		return nil
	}
	return d.Plan.Narratives
}
