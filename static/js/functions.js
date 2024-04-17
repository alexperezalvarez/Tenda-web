//fetch chatgpt

function enviar_datos(url, datos, callback) {
  const csrftoken = $("[name=csrfmiddlewaretoken]").val(); // obtener el token CSRF del input escondido de la pagina

  fetch(url, {
    method: "POST",
    body: JSON.stringify(datos), // Convierte los datos en JSON para poder procesarlos en la vista
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      callback(data);
    })
    .catch((error) => {
      //****************** que hubo un error
      const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
        didOpen: (toast) => {
          toast.addEventListener("mouseenter", Swal.stopTimer);
          toast.addEventListener("mouseleave", Swal.resumeTimer);
        },
      });

      Toast.fire({
        icon: "error",
        title: `${error}`,
      });
      //*************
    });
}

function carritoAcciones(itemId, url, accion) {
  let datos = {
    pk: itemId,
    action: accion,
  };
  enviar_datos(url, datos, function (data) {
    //funcion que realiza acciones despues de la petición
    if (data["error"]) {
      //****************** que hubo un error
      const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 1500,
        timerProgressBar: true,
        didOpen: (toast) => {
          toast.addEventListener("mouseenter", Swal.stopTimer);
          toast.addEventListener("mouseleave", Swal.resumeTimer);
        },
      });

      Toast.fire({
        icon: "error",
        title: `${data["error"]}`,
      });
      //*************
    } else {
      if (accion == "add_cart") {
        //****************** de que se agrego correctamente
        const Toast = Swal.mixin({
          toast: true,
          position: "bottom-end",
          showConfirmButton: false,
          timer: 1500,
          timerProgressBar: true,
          didOpen: (toast) => {
            toast.addEventListener("mouseenter", Swal.stopTimer);
            toast.addEventListener("mouseleave", Swal.resumeTimer);
          },
        });

        Toast.fire({
          icon: "success",
          title: `${data["mensaje"]}`,
        });
        //*************
        const pTotal = document.getElementById("cart-total"); //obtengo el p del carrito
        pTotal.innerHTML = `${data["can_carrito"]}`; //le pongo la cantidad

        //si es alguna de las 3 acciones del carrito lo pongo aqui
      } else if (accion == "eliminar") {
        var trElim = document.getElementById("item-" + itemId); //obtengo el tr del item y lo quito si la petición de eliminar es correcta
        if (trElim) {
          //para que al eliminar rapido no se demore y salga un error
          trElim.remove();
        }
      } else if (accion == "aumentar" || accion == "disminuir") {
        const cantidad = document.getElementById(`product/${itemId}`); //donde va la cantidad
        const total = document.getElementById(`total_product/${itemId}`); //donde va el total
        cantidad.innerHTML = `${data["can_cantidad"]}`;
        totalN = data["can_total"].toLocaleString("es-ES", {
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        });
        total.innerHTML = `${totalN}`;
        //quitarle el disabled al boton
        if (accion == "aumentar") {
          const aumentar = document.getElementById(`${itemId}/aumentar`);
          aumentar.removeAttribute("disabled");
        } else {
          const disminuir = document.getElementById(`${itemId}/disminuir`);
          disminuir.removeAttribute("disabled");
        }
      }
      if (
        accion == "aumentar" ||
        accion == "disminuir" ||
        accion == "eliminar"
      ) {
        //independientemente de la accion, eliminar, aumentar o disminuir, se modifica el total del checkout
        const checkoutTotal = document.getElementById(`checkout_total`);
        checkTotalN = data["check_total"].toLocaleString("es-ES", {
          //para convertirlo a numero natural o el intcomma de django
          minimumFractionDigits: 1,
          maximumFractionDigits: 1,
        });
        checkoutTotal.innerHTML = `${checkTotalN}`;
        if (data["check_total"] == 0) {
          //si el el total del carrito es 0, remplazo todo el contenido y pongo un mensaje
          const contenedorABorrar = document.getElementById("contenedor_todo");
          contenedorABorrar.innerHTML =
            "<h2>No hay productos en el carrito</h2>";
        }
      }
    }
  });
}
