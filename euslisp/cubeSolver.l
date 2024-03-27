(load "rcb4rosinterface.l")
(load "config.l")

(defun gripper-angle(arm angle)
  (send *robot* arm :gripper-r :joint-angle angle)
  (send *robot* arm :gripper2-r :joint-angle angle)
  )

(defun grasp(arm)
  (gripper-angle arm 23)
  (send *ri* :angle-vector (send *robot* :angle-vector) 500)
  )

(defun release(arm)
  (gripper-angle arm 55)
  (send *ri* :angle-vector (send *robot* :angle-vector) 200)
  )

(defun angle(arm angle)
  (let ((angle (+ angle (if (eq arm :rarm) *rwr-offset* *lwr-offset*)))
	(wr (send *robot* arm :wrist-r))
	da n)
    (setq da (- angle (send wr :joint-angle))) 
    (setq n (round (/ (abs da) 30)))
    (send wr :joint-angle angle)
    (send *ri* :angle-vector (send *robot* :angle-vector) (* n 200))
  ))

(defun command-callback (req)
  (let ((com (send req :command))
        (res (send req :response))
        )
    (print com)
    (eval (read-from-string com))
    (send res :success t)
    res
    )
  )

(defun start-command-server ()
  (print "start command server")
  (while t
    (ros::spin-once) ;; need to execute callbacks
    (ros::sleep)
    )
  )

(defun demo()
  (make-kxr-robot "kxrl2l2a6h2m")
  (send *ri* :com-init)
  (start-command-server)
  )

(ros::roseus-add-srvs "kxr_cube_solver")
(ros::roseus "command_server")
(ros::rate 10)
(ros::advertise-service "~send_command" kxr_cube_solver::SendCommand #'command-callback)
(demo)
