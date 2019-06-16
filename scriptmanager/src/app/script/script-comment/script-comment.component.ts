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

  }

}
