subroutine fortran_apply_gradient(x, x_old, g, lr, n, ndim)
    implicit none
    integer :: n, ndim
    double precision, dimension(n, ndim) :: x, x_old
    double precision, dimension(n, ndim) :: g
    double precision :: lr

    integer :: i, j
    !f2py intent(hide) :: n, ndim
    !f2py intent(out) :: x
    !f2py intent(in) :: x_old, g, lr

    do i = 1, n
        do j = 1, ndim
            x(i, j) = x_old(i, j) - lr*g(i, j)
        end do
    end do

end subroutine
