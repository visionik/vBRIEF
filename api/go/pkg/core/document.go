package core

// Document manipulation methods for editing vBRIEF documents after creation.

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

// AddPlanItem adds a new plan item to the Plan.
func (d *Document) AddPlanItem(item PlanItem) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	d.Plan.Items = append(d.Plan.Items, item)
	return nil
}

// UpdatePlanItem updates an existing plan item at the specified index.
func (d *Document) UpdatePlanItem(index int, item PlanItem) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Items) {
		return ErrInvalidIndex
	}
	d.Plan.Items[index] = item
	return nil
}

// UpdatePlanItemStatus updates the status of a plan item at the specified index.
func (d *Document) UpdatePlanItemStatus(index int, status PlanItemStatus) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Items) {
		return ErrInvalidIndex
	}
	d.Plan.Items[index].Status = status
	return nil
}

// RemovePlanItem removes a plan item at the specified index.
func (d *Document) RemovePlanItem(index int) error {
	if d.Plan == nil || index < 0 || index >= len(d.Plan.Items) {
		return ErrInvalidIndex
	}
	d.Plan.Items = append(d.Plan.Items[:index], d.Plan.Items[index+1:]...)
	return nil
}

// AddNarrative adds or updates a narrative in the Plan.
func (d *Document) AddNarrative(key string, content string) error {
	if d.Plan == nil {
		return ErrNoPlan
	}
	if d.Plan.Narratives == nil {
		d.Plan.Narratives = make(map[string]string)
	}
	d.Plan.Narratives[key] = content
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

// GetPlanItems returns all plan items (nil-safe).
func (d *Document) GetPlanItems() []PlanItem {
	if d.Plan == nil {
		return nil
	}
	return d.Plan.Items
}

// GetNarratives returns all narratives (nil-safe).
func (d *Document) GetNarratives() map[string]string {
	if d.Plan == nil {
		return nil
	}
	return d.Plan.Narratives
}
