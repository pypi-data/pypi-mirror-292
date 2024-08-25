subroutine fortran_update_velocity_3(velocity3_out, velocity3, velocity1, velocity2, g1, g2, sub_swarm, &
                                     w, c1, c2, pbest, gbest, eps, seed, n, ndim)
    implicit none
    double precision, dimension(n, ndim) :: velocity1, velocity2, velocity3, velocity3_out, sub_swarm
    double precision, dimension(1, ndim) :: pbest, gbest
    double precision, dimension(n, 1) :: w, g1, g2
    double precision :: c1, c2, eps
    integer :: n, ndim
    integer, optional :: seed

    !f2py intent(out) :: velocity3_out
    !f2py intent(in) :: velocity3
    !f2py intent(in)    :: sub_swarm, w, c1, c2, pbest, gbest, seed, velocity2, velocity1, g1, g2, eps
    !f2py intent(hide)  :: n, ndim

    double precision, dimension(n) :: random1, random2
    integer, dimension(:), allocatable :: seed_array
    double precision :: gg, gg1, gg2
    integer :: i, d, nseed

    ! set the seed
    if (present(seed)) then
        call random_seed(size=nseed)
        allocate (seed_array(nseed))
        seed_array = seed
        call random_seed(put=seed_array)
    end if

    ! generate random arrays ahead
    call random_number(random1)
    call random_number(random2)

    ! update velocities
    do i = 1, n

        gg = g1(i, 1) + g2(i, 1)
        gg1 = gg/(g1(i, 1) + eps)
        gg2 = gg/(g2(i, 1) + eps)

        do d = 1, ndim
            velocity3_out(i, d) = w(i, 1)*(velocity3(i, d) + gg1*velocity1(i, d) + gg2*velocity2(i, d)) &
                                  + c1*random1(i)*(pbest(1, d) - sub_swarm(i, d)) &
                                  + c2*random2(i)*(gbest(1, d) - sub_swarm(i, d))
        end do
    end do
end subroutine

subroutine fortran_update_velocity(velocity_out, velocity, sub_swarm, w, c1, c2, pbest, gbest, seed, n, ndim)
    implicit none
    double precision, dimension(n, ndim) :: velocity_out, velocity, sub_swarm
    double precision, dimension(1, ndim) :: pbest, gbest
    double precision, dimension(n, 1) :: w
    double precision :: c1, c2
    integer :: n, ndim
    integer, optional :: seed

    !f2py intent(out) :: velocity_out
    !f2py intent(in) :: velocity
    !f2py intent(in)    :: sub_swarm, w, c1, c2, pbest, gbest, seed
    !f2py intent(hide)  :: n, ndim

    double precision, dimension(n) :: random1, random2
    integer, dimension(:), allocatable :: seed_array
    integer :: i, d, nseed

    ! set the seed
    if (present(seed)) then
        call random_seed(size=nseed)
        allocate (seed_array(nseed))
        seed_array = seed
        call random_seed(put=seed_array)
    end if

    ! generate random arrays ahead
    call random_number(random1)
    call random_number(random2)

    ! update velocities
    do i = 1, n
        do d = 1, ndim
            velocity_out(i, d) = w(i, 1)*velocity(i, d) &
                                 + c1*random1(i)*(pbest(1, d) - sub_swarm(i, d)) &
                                 + c2*random2(i)*(gbest(1, d) - sub_swarm(i, d))
        end do
    end do
end subroutine

subroutine fortran_linear_inertia(w_out, current_iter, max_iter, w_min, w_max)
    implicit none
    double precision :: w_out, w_min, w_max
    integer :: current_iter, max_iter
    !f2py intent(out) :: w_out
    !f2py intent(in) :: current_iter, max_iter, w_min, w_max

    w_out = (w_max - w_min)*(max_iter - current_iter)/max_iter + w_min
end subroutine

subroutine fortran_mscpso_inertia(w_out, current_iter, max_iter, w_min, w_max, f, f_min, f_avg, n)
    implicit none
    double precision, dimension(n, 1) :: f, w_out
    double precision :: w_min, w_max
    double precision :: f_min, f_avg
    integer :: current_iter, max_iter, n
    !f2py intent(out) :: w_out
    !f2py intent(in) :: current_iter, max_iter, w_min, w_max, f, f_min, f_avg
    !f2py intent(hide) :: n

    double precision :: f_i
    integer :: i

    do i = 1, n
        f_i = f(i, 1)
        if (f_i >= f_avg) then
            w_out(i, 1) = w_max
        elseif (f_avg > f_i .and. f_i > f_avg/2) then
            w_out(i, 1) = w_min + (f_i - f_min)*(w_max - w_min)/(f_avg/2 - f_min)
        else
            call fortran_linear_inertia(w_out(i, 1), current_iter, max_iter, w_min, w_max)
        end if
    end do
end subroutine
