import { Component,Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {

  @Input() comments:any;
  constructor() { }



  ngOnInit() {
    // this.route.params.subscribe(params => {
    //   this.id = +params['id'];
    // });
    // console.log(this.comments);
    // return this.comments;


  }

}
