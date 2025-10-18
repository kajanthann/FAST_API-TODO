const form = document.getElementById("todoForm");
const todoList = document.getElementById("todoList");
const titleInput = document.getElementById("title");
const descInput = document.getElementById("description");
const todoIdInput = document.getElementById("todoId");
const cancelBtn = document.getElementById("cancelEdit");

// Load todos
async function loadTodos() {
    const response = await fetch("/todo");
    const todos = await response.json();
    todoList.innerHTML = "";
    todos.forEach(addTodoToList);
}

// Add todo to list
function addTodoToList(todo) {
    const li = document.createElement("li");

    const textSpan = document.createElement("span");
    textSpan.textContent = `${todo.title} - ${todo.description || ""}`;
    if (todo.completed) textSpan.classList.add("completed");

    // Edit button
    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.classList.add("edit-btn");
    editBtn.onclick = (e) => {
        e.stopPropagation();
        titleInput.value = todo.title;
        descInput.value = todo.description;
        todoIdInput.value = todo.id;
        form.querySelector('button[type="submit"]').textContent = "Update Todo";
        cancelBtn.style.display = "inline-block";
    };

    // Delete button
    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.classList.add("delete-btn");
    delBtn.onclick = async (e) => {
        e.stopPropagation();
        await fetch(`/todo/${todo.id}`, { method: "DELETE" });
        loadTodos();
    };

    const buttonWrapper = document.createElement("div");
    buttonWrapper.classList.add("button-wrapper");
    buttonWrapper.appendChild(editBtn);
    buttonWrapper.appendChild(delBtn);

    li.appendChild(textSpan);
    li.appendChild(buttonWrapper);
    todoList.appendChild(li);
}

// Form submit (Create / Update)
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const todoId = todoIdInput.value;
    const payload = {
        title: titleInput.value,
        description: descInput.value
    };

    if (todoId) {
        await fetch(`/todo/${todoId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    } else {
        await fetch("/todo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    }

    form.reset();
    todoIdInput.value = "";
    form.querySelector('button[type="submit"]').textContent = "Add Todo";
    cancelBtn.style.display = "none";
    loadTodos();
});

// Cancel edit
cancelBtn.addEventListener("click", () => {
    form.reset();
    todoIdInput.value = "";
    form.querySelector('button[type="submit"]').textContent = "Add Todo";
    cancelBtn.style.display = "none";
});

// Initial load
loadTodos();
